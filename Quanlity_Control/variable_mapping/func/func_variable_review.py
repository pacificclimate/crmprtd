"""Batch review of canonical variables, separate from the single-variable notebook."""
from __future__ import annotations

import json
from numbers import Integral
from pathlib import Path
import shutil
from tempfile import mkdtemp
from uuid import uuid4

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import sqlalchemy as sa

from func_variable_mapping import (
    CANONICAL_RULES, CANONICAL_VARIABLES, add_network_station_counts,
    apply_canonical_rule,
    fetch_candidate_observations, select_candidate_stations,
)


SOURCE_VARS_TIME_SCALES_BY_NETWORK = {
    1: {
        427: 'daily', 428: 'daily', 429: 'daily', 430: 'daily',
        431: 'daily', 432: 'daily',
    },
    2: {
        433: 'daily', 434: 'hourly', 435: 'daily', 436: 'hourly',
        440: 'hourly', 441: 'hourly', 442: 'hourly', 443: 'hourly',
        450: 'daily', 451: 'daily', 720: 'hourly', 721: 'hourly',
        722: 'hourly', 726: 'hourly', 727: 'hourly', 728: 'hourly',
        732: 'daily',
    },
    3: {
        452: 'daily', 453: 'hourly', 454: 'daily', 456: 'daily',
        459: 'daily', 460: 'daily', 461: 'daily', 462: 'daily',
    },
    5: {
        463: 'daily', 464: 'daily', 465: 'daily', 466: 'daily',
        467: 'daily', 468: 'daily', 655: 'hourly', 657: 'hourly',
        675: 'hourly', 677: 'hourly', 1328: 'hourly', 1329: 'hourly',
        1331: 'hourly', 1332: 'hourly', 1333: 'hourly', 1334: 'daily',
    },
    6: {
        469: 'daily', 470: 'daily', 471: 'daily', 1198: 'hourly',
        1201: 'hourly', 1205: 'hourly', 1206: 'hourly', 1210: 'daily',
    },
    10: {493: 'daily', 494: 'daily', 495: 'daily'},
    11: {
        501: 'hourly', 503: 'hourly', 529: 'daily', 530: 'hourly',
        531: 'hourly', 832: 'hourly', 1266: 'hourly', 1349: 'hourly',
        1350: 'hourly', 1354: 'hourly',
    },
    12: {
        496: 'hourly', 497: 'hourly', 711: 'hourly', 712: 'hourly',
        718: 'hourly', 736: 'hourly',
    },
    19: {
        542: 'hourly', 544: 'daily', 545: 'daily', 546: 'daily',
        547: 'daily', 548: 'daily',
    },
    9: {472: 'hourly', 473: 'hourly', 693: 'hourly'},
}


def candidate_source_time_scales(candidate_mappings, network_id):
    """Resolve active candidate cadences from saved values, then legacy data."""
    active = candidate_mappings.loc[
        candidate_mappings['mapping_status'].ne('excluded')].copy()
    active_ids = sorted({int(value) for value in active['vars_id']})
    legacy = SOURCE_VARS_TIME_SCALES_BY_NETWORK.get(int(network_id), {})
    resolved = {}
    if 'source_time_scale' in active.columns:
        for row in active[['vars_id', 'source_time_scale']].itertuples(index=False):
            if pd.notna(row.source_time_scale):
                value = str(row.source_time_scale).strip().lower()
                if value not in {'hourly', 'daily'}:
                    raise ValueError(
                        f"Invalid source_time_scale {row.source_time_scale!r} "
                        f"for vars_id {int(row.vars_id)}."
                    )
                resolved[int(row.vars_id)] = value
    for vars_id in active_ids:
        if vars_id not in resolved and vars_id in legacy:
            resolved[vars_id] = legacy[vars_id]
    missing = sorted(set(active_ids) - set(resolved))
    if missing:
        raise ValueError(
            f"Missing daily/hourly labels for active candidate vars_ids: {missing}. "
            "Rerun 0.candidate_discovery.ipynb or add a reviewed override."
        )
    return resolved


def format_candidate_review(frame):
    """Put the decision after aggregation and priority at the far right."""
    frame = frame.drop(columns=['mapping_status', 'total_station_count'], errors='ignore')
    columns = [name for name in frame.columns
               if name not in ['decision', 'latest_observation_from_cutoff', 'priority']]
    if 'decision' in frame.columns:
        position = columns.index('daily_aggregation') + 1 if 'daily_aggregation' in columns else len(columns)
        columns.insert(position, 'decision')
    columns += [name for name in ['latest_observation_from_cutoff', 'priority']
                if name in frame.columns]
    return frame[columns]


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f'{name} must be a positive integer.')


def _promote_latest_review(staging_dir, output_dir):
    """Replace latest_review with a completed staging directory, with rollback."""
    output_dir = Path(output_dir)
    latest_dir = output_dir / 'latest_review'
    backup_dir = output_dir / f'.review_backup_{uuid4().hex}'
    had_latest = latest_dir.exists()
    try:
        if had_latest:
            latest_dir.rename(backup_dir)
        Path(staging_dir).rename(latest_dir)
    except Exception:
        if had_latest and backup_dir.exists() and not latest_dir.exists():
            backup_dir.rename(latest_dir)
        raise
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    return latest_dir.resolve()


def _order_rule_columns(frame):
    """Keep recent-source evidence directly after the selected source IDs."""
    adjacent = ['source_vars_ids', 'source_vars_time_scales', 'candidate_vars_ids',
                'recent_source_vars_ids',
                'recent_source_latest_observations']
    columns = [name for name in frame.columns if name not in adjacent]
    if 'source_vars_ids' not in frame.columns:
        return frame
    position = frame.columns.get_loc('source_vars_ids')
    columns[position:position] = [name for name in adjacent if name in frame.columns]
    return frame.loc[:, columns]


def save_source_selection_summary(networks_dir):
    """Summarize automatic versus preserved/manual final source selections."""
    networks_dir = Path(networks_dir)
    rows = []
    for rules_path in networks_dir.glob(
            'network_*/net*_final_variable_rules.csv'):
        rules = pd.read_csv(rules_path)
        network_id = int(float(rules.network_id.iloc[0])) if not rules.empty else None
        registry_path = rules_path.parent / f'net{network_id}_candidate_mappings.csv'
        active_candidates = {}
        if registry_path.exists():
            registry = pd.read_csv(registry_path)
            registry = registry.loc[~registry.mapping_status.eq('excluded')]
            active_candidates = registry.groupby('canonical_variable').vars_id.apply(
                lambda values: {int(value) for value in values}).to_dict()
        for rule in rules.to_dict('records'):
            source_ids = sorted(int(value) for value in json.loads(
                rule.get('source_vars_ids') or '[]'))
            recent_ids = {int(value) for value in json.loads(
                rule.get('recent_source_vars_ids') or '[]')}
            automatic_ids = sorted(set(source_ids) & recent_ids)
            remaining_ids = set(source_ids) - set(automatic_ids)
            variable = rule['canonical_variable']
            candidates = active_candidates.get(variable)
            if candidates is None:
                candidates = {int(value) for value in json.loads(
                    rule.get('candidate_vars_ids') or '[]')}
            single_candidate_ids = sorted(
                remaining_ids & candidates if len(candidates) == 1 else set())
            manual_ids = sorted(remaining_ids - set(single_candidate_ids))
            rows.append({
                'network_id': int(float(rule['network_id'])),
                'canonical_variable': rule['canonical_variable'],
                'source_vars_ids': json.dumps(source_ids),
                'source_vars_time_scales': rule.get('source_vars_time_scales', '{}'),
                'automatically_recognized_source_vars_ids': json.dumps(automatic_ids),
                'single_candidate_saved_source_vars_ids': json.dumps(
                    single_candidate_ids),
                'manually_saved_source_vars_ids': json.dumps(manual_ids),
                'candidate_vars_ids': rule.get('candidate_vars_ids', '[]'),
                'source_checked_at_utc': rule.get('source_checked_at_utc', ''),
                'classification_basis': (
                    'latest recent-data recognition; otherwise sole active candidate; '
                    'remaining saved sources are classified as manual'),
            })
    columns = [
        'network_id', 'canonical_variable', 'source_vars_ids',
        'source_vars_time_scales',
        'automatically_recognized_source_vars_ids',
        'single_candidate_saved_source_vars_ids',
        'manually_saved_source_vars_ids', 'candidate_vars_ids',
        'source_checked_at_utc', 'classification_basis',
    ]
    summary = pd.DataFrame(rows, columns=columns)
    if not summary.empty:
        summary = summary.sort_values(
            ['network_id', 'canonical_variable']).reset_index(drop=True)
    output_path = networks_dir / 'all_networks_source_vars_summary.csv'
    summary.to_csv(output_path, index=False)
    return summary


def _check_recent(engine, candidate_ids, station_ids, network_id, cutoff):
    query = sa.text("""
        SELECT s.station_id, v.vars_id,
               latest.obs_time AS latest_observation_from_cutoff
        FROM meta_station s CROSS JOIN meta_vars v
        LEFT JOIN LATERAL (
            SELECT o.obs_time FROM obs_raw o
            JOIN meta_history h USING (history_id)
            WHERE h.station_id = s.station_id AND o.vars_id = v.vars_id
              AND o.datum IS NOT NULL AND o.obs_time >= :auto_keep_from
            ORDER BY o.obs_time DESC LIMIT 1
        ) latest ON TRUE
        WHERE s.network_id = :network_id AND s.station_id IN :station_ids
          AND v.vars_id IN :vars_ids
        ORDER BY v.vars_id, s.station_id
    """).bindparams(sa.bindparam('vars_ids', expanding=True),
                    sa.bindparam('station_ids', expanding=True))
    conditions = pd.read_sql(query, engine, params={
        'vars_ids': candidate_ids, 'station_ids': station_ids,
        'network_id': network_id,
        'auto_keep_from': pd.Timestamp(cutoff).to_pydatetime(),
    })
    conditions['latest_observation_from_cutoff'] = pd.to_datetime(
        conditions['latest_observation_from_cutoff'])
    conditions['has_recent_non_null_observations'] = (
        conditions['latest_observation_from_cutoff'].notna())
    coverage = conditions.groupby('vars_id', as_index=False).agg(
        total_station_count=('station_id', 'nunique'),
        recent_non_null_station_count=('has_recent_non_null_observations', 'sum'),
        latest_observation_from_cutoff=('latest_observation_from_cutoff', 'max'),
    )
    return conditions, coverage


def _notice(pdf, variable, message):
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis('off')
    ax.set_title(variable)
    ax.text(.5, .5, message, ha='center', va='center', transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _plot_variable(clean, variable, time_pdf, cdf_pdf,
                   source_vars_time_scales=None):
    """One page per station in each report, preserving readable figure sizes."""
    source_vars_time_scales = source_vars_time_scales or {}
    if clean.empty:
        for pdf in (time_pdf, cdf_pdf):
            _notice(pdf, variable, 'No plausible data for the selected plot stations.')
        return
    ylabel = {'celsius': 'Temperature (°C)', 'mm': 'Amount (mm)',
              'cm': 'Amount (cm)'}[CANONICAL_RULES[variable].unit]
    positive_only = variable in {'precipitation_amount', 'snowfall_amount'}
    time_values = pd.to_datetime(clean['obs_time'], errors='coerce').dropna()
    shared_time_range = None
    if not time_values.empty:
        start, end = time_values.min(), time_values.max()
        if start == end:
            start, end = start - pd.Timedelta(hours=12), end + pd.Timedelta(hours=12)
        shared_time_range = (start, end)
    for station_id, frame in clean.groupby('station_id'):
        title = f"{variable} — {frame['station_name'].iloc[0]} (station {station_id})"
        for mode, pdf in [('time_series', time_pdf), ('cdf', cdf_pdf)]:
            fig, ax = plt.subplots(figsize=(14, 5))
            any_values = False
            for (vid, name), data in frame.groupby(['vars_id', 'net_var_name']):
                label = f'{vid} — {name}'
                time_scale = source_vars_time_scales.get(int(vid))
                if time_scale:
                    label += f' ({time_scale})'
                if mode == 'time_series':
                    data = data.sort_values('obs_time')
                    ax.plot(data.obs_time, data.datum, linewidth=1, alpha=.8, label=label)
                    any_values = True
                else:
                    values = data.datum.dropna()
                    if positive_only:
                        values = values[values > 0]
                    values = np.sort(values.to_numpy())
                    if len(values):
                        ax.step(values, np.arange(1, len(values) + 1) / len(values),
                                where='post', label=label)
                        any_values = True
            if mode == 'time_series':
                ax.set(xlabel='Time', ylabel=ylabel, title=f'{title}: time series')
                if shared_time_range is not None:
                    ax.set_xlim(*shared_time_range)
            else:
                if positive_only:
                    ax.set_xscale('log')
                ax.set(xlabel=ylabel + (' — positive values, log scale' if positive_only else ''),
                       ylabel='Cumulative proportion', title=f'{title}: ECDF')
            if any_values:
                ax.legend()
            else:
                ax.text(.5, .5, 'No positive values for ECDF', ha='center',
                        transform=ax.transAxes)
            fig.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)


def run_variable_reviews(engine, candidate_mappings, output_dir, *, network_id=2,
                         variables=None, plot_station_limit=10,
                         source_station_limit=20, random_seed=None,
                         auto_keep_from='2026-01-01',
                         source_vars_time_scales=None):
    """Review every requested variable once; return serializable results for saving.

    Output replaces ``latest_review`` inside ``output_dir`` only after the run
    succeeds. Automatic keeps and latest dates describe only the sampled stations,
    not the network as a whole. This does not save final rules; manual decisions
    are applied independently by save_review_rules.
    """
    _positive_integer(plot_station_limit, 'plot_station_limit')
    _positive_integer(source_station_limit, 'source_station_limit')
    variables = list(CANONICAL_VARIABLES if variables is None else variables)
    if not variables or len(set(variables)) != len(variables):
        raise ValueError('Choose a nonempty list of distinct canonical variables.')
    unknown = set(variables) - set(CANONICAL_VARIABLES)
    if unknown:
        raise ValueError(f'Unknown canonical variables: {sorted(unknown)}')
    cutoff = pd.Timestamp(auto_keep_from).isoformat()
    if pd.isna(pd.Timestamp(auto_keep_from)):
        raise ValueError('auto_keep_from must be a valid date.')
    output_dir = Path(output_dir)
    require_candidate_time_scales = source_vars_time_scales is not None
    source_vars_time_scales = {
        int(vars_id): str(scale).strip().lower()
        for vars_id, scale in (source_vars_time_scales or {}).items()
    }
    invalid_scales = {
        vars_id: scale for vars_id, scale in source_vars_time_scales.items()
        if scale not in {'hourly', 'daily'}
    }
    if invalid_scales:
        raise ValueError(
            f'source_vars_time_scales must use hourly or daily: {invalid_scales}')
    mappings = candidate_mappings.loc[candidate_mappings.network_id == network_id]
    if ("network_station_count" not in mappings or
            mappings["network_station_count"].isna().any()):
        mappings = add_network_station_counts(
            engine, mappings, network_id=int(network_id))
    if require_candidate_time_scales:
        plotted_candidate_ids = {
            int(value) for value in mappings.loc[
                ~mappings.mapping_status.eq('excluded'), 'vars_id']
        }
        missing_time_scales = plotted_candidate_ids - set(source_vars_time_scales)
        if missing_time_scales:
            raise ValueError(
                'Missing daily/hourly labels for active candidate vars_ids: '
                f'{sorted(missing_time_scales)}')
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = Path(mkdtemp(prefix='.review_staging_', dir=output_dir)).resolve()
    latest_dir = (output_dir / 'latest_review').resolve()
    output_prefix = f'net{int(network_id)}_'
    results = {'run_dir': str(run_dir), 'network_id': int(network_id),
               'candidate_ids': {}, 'excluded_candidate_ids': {},
               'source_vars_time_scales': source_vars_time_scales,
               'output_prefix': output_prefix, 'rules': [], 'status': []}
    reviews, qc_tables, condition_tables = [], [], []
    with PdfPages(run_dir / f'{output_prefix}time_series.pdf') as time_pdf, \
         PdfPages(run_dir / f'{output_prefix}cdf.pdf') as cdf_pdf:
        for variable in variables:
            print(f'Reviewing {variable}...', flush=True)
            variable_mappings = mappings.loc[
                mappings.canonical_variable == variable
            ].drop_duplicates('vars_id').copy()
            excluded_ids = sorted(int(value) for value in variable_mappings.loc[
                variable_mappings.mapping_status.eq('excluded'), 'vars_id'])
            candidates = variable_mappings.loc[
                ~variable_mappings.mapping_status.eq('excluded')].copy()
            candidate_ids = sorted(int(value) for value in candidates.vars_id)
            all_candidate_ids = sorted(int(value) for value in variable_mappings.vars_id)
            results['candidate_ids'][variable] = candidate_ids
            results['excluded_candidate_ids'][variable] = excluded_ids
            status = dict(canonical_variable=variable, status='ok', eligible_station_count=0,
                          source_station_count=0, plot_station_ids=[],
                          station_selection_method='not_applicable')
            results['status'].append(status)
            if candidates.empty:
                status['status'] = 'no_candidates'
            else:
                eligible = select_candidate_stations(
                    engine, candidate_ids, network_id=network_id, limit=None,
                    match='all')
                status['station_selection_method'] = 'all_candidates'
                if eligible.empty:
                    eligible = select_candidate_stations(
                        engine, candidate_ids, network_id=network_id, limit=None,
                        match='any')
                    status['station_selection_method'] = 'any_candidate_fallback'
                status['eligible_station_count'] = len(eligible)
                if eligible.empty:
                    status['status'] = 'no_matching_stations'
            if status['status'] != 'ok':
                for pdf in (time_pdf, cdf_pdf):
                    _notice(pdf, variable, status['status'].replace('_', ' '))
                if len(candidate_ids) == 1:
                    checked_at = pd.Timestamp.now(tz='UTC').isoformat()
                    results['rules'].append(dict(
                        network_id=int(network_id), canonical_variable=variable,
                        source_vars_ids='[]', source_vars_time_scales='{}',
                        candidate_vars_ids=json.dumps(all_candidate_ids),
                        auto_keep_from=auto_keep_from,
                        source_check_scope=status['station_selection_method'],
                        source_station_limit=int(source_station_limit),
                        source_random_seed=random_seed, source_station_count=0,
                        source_station_ids='[]', source_checked_at_utc=checked_at,
                        recent_source_vars_ids='[]',
                        recent_source_latest_observations='{}',
                        time_match='exact_timestamp', overlap_method='mean',
                        single_source_method='use_available',
                    ))
                continue

            def sample_ids(limit):
                return sorted(int(value) for value in eligible.sample(
                    n=min(limit, len(eligible)), random_state=random_seed,
                    replace=False).station_id)

            source_ids, plot_ids = sample_ids(source_station_limit), sample_ids(plot_station_limit)
            status.update(source_station_count=len(source_ids), plot_station_ids=plot_ids)
            conditions, coverage = _check_recent(engine, candidate_ids, source_ids, network_id, cutoff)
            checked_at = pd.Timestamp.now(tz='UTC').isoformat()
            recent = coverage.loc[coverage.recent_non_null_station_count > 0]
            auto_ids = sorted(int(value) for value in recent.vars_id)
            recent = recent.loc[recent.vars_id.astype(int).isin(auto_ids)]
            latest = {str(int(row.vars_id)): pd.Timestamp(row.latest_observation_from_cutoff).isoformat()
                      for row in recent.itertuples(index=False)}
            candidate_review = candidates.merge(coverage, on='vars_id', how='left', validate='one_to_one')
            def decision(vars_id):
                if int(vars_id) in auto_ids:
                    return 'automatic keep'
                return 'manual decision'

            candidate_review['decision'] = candidate_review.vars_id.map(decision)
            candidate_review['source_checked_at_utc'] = checked_at
            reviews.append(format_candidate_review(candidate_review))
            condition_tables.append(conditions.assign(network_id=network_id, canonical_variable=variable))
            results['rules'].append(dict(
                network_id=int(network_id), canonical_variable=variable,
                source_vars_ids=json.dumps(auto_ids),
                source_vars_time_scales=json.dumps({
                    str(vars_id): source_vars_time_scales[vars_id]
                    for vars_id in auto_ids if vars_id in source_vars_time_scales
                }, sort_keys=True),
                candidate_vars_ids=json.dumps(all_candidate_ids),
                auto_keep_from=auto_keep_from,
                source_check_scope='random_stations_with_all_candidates',
                source_station_limit=int(source_station_limit), source_random_seed=random_seed,
                source_station_count=len(source_ids), source_station_ids=json.dumps(source_ids),
                source_checked_at_utc=checked_at, recent_source_vars_ids=json.dumps(auto_ids),
                recent_source_latest_observations=json.dumps(latest, sort_keys=True),
                time_match='exact_timestamp', overlap_method='mean', single_source_method='use_available',
            ))
            observations = fetch_candidate_observations(engine, candidate_ids, plot_ids)
            clean, qc = apply_canonical_rule(observations, variable)
            qc_tables.append(qc.assign(network_id=network_id, canonical_variable=variable))
            if clean.empty:
                status['status'] = 'no_plausible_plot_data'
            _plot_variable(
                clean, variable, time_pdf, cdf_pdf,
                source_vars_time_scales=source_vars_time_scales)

    for name, tables, columns in [
        ('candidate_review', reviews, ['canonical_variable', 'vars_id', 'total_station_count', 'recent_non_null_station_count']),
        ('qc_summary', qc_tables, ['canonical_variable', 'vars_id']),
        ('station_conditions', condition_tables, ['canonical_variable', 'vars_id', 'station_id']),
    ]:
        frame = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame(columns=columns)
        keys = [key for key in ['canonical_variable', 'vars_id', 'station_id'] if key in frame]
        frame.sort_values(keys).to_csv(
            run_dir / f'{output_prefix}{name}.csv', index=False)
    pd.DataFrame(results['status']).to_csv(
        run_dir / f'{output_prefix}run_summary.csv', index=False)
    results['run_dir'] = str(latest_dir)
    (run_dir / f'{output_prefix}review_results.json').write_text(
        json.dumps(results, indent=2) + '\n')
    run_dir = _promote_latest_review(run_dir, output_dir)
    print(f'Review complete: {run_dir}', flush=True)
    return results


def save_review_rules(results, manual_source_ids, rules_path):
    """Apply manual additions to completed reviews and upsert rules without queries.

    Existing selections are preserved on ordinary reruns. A change to the recorded
    manual IDs is treated as a deliberate addition or removal. All manual IDs are
    validated before any CSV write. Legacy detailed-condition/save-time columns are
    removed.
    """
    unknown = set(manual_source_ids) - set(results['candidate_ids'])
    if unknown:
        raise ValueError(f'Manual choices name unreviewed variables: {sorted(unknown)}')
    completed = {row['canonical_variable'] for row in results['rules']}
    for variable, ids in manual_source_ids.items():
        if any(isinstance(vid, bool) or not isinstance(vid, Integral) for vid in ids):
            raise ValueError(f'Manual IDs must be integers for {variable}.')
        invalid = set(ids) - set(results['candidate_ids'][variable])
        if invalid or (ids and variable not in completed):
            raise ValueError(f'Invalid manual selection for {variable}: {ids}')
    rows = []
    for original in results['rules']:
        row = original.copy()
        variable = row['canonical_variable']
        excluded = set(results.get('excluded_candidate_ids', {}).get(variable, []))
        if not excluded:
            excluded = set(json.loads(row.get('excluded_source_vars_ids', '[]')))
        chosen = sorted((set(json.loads(row['recent_source_vars_ids'])) |
                         {int(vid) for vid in manual_source_ids.get(variable, [])}) -
                        excluded)
        active_candidates = sorted(set(results['candidate_ids'][variable]) - excluded)
        if not chosen and len(active_candidates) == 1:
            chosen = active_candidates
        if not chosen:
            print(f'No sources selected for {variable}; existing rule left unchanged.')
            continue
        row['source_vars_ids'] = json.dumps(chosen)
        configured_scales = {
            int(vars_id): scale for vars_id, scale in
            results.get('source_vars_time_scales', {}).items()
        }
        row['source_vars_time_scales'] = json.dumps({
            str(vars_id): configured_scales[vars_id]
            for vars_id in chosen if vars_id in configured_scales
        }, sort_keys=True)
        if 'candidate_vars_ids' not in row:
            row['candidate_vars_ids'] = json.dumps(sorted(
                set(results['candidate_ids'][variable]) | excluded))
        row.pop('excluded_source_vars_ids', None)
        rows.append(row)
    rules_path = Path(rules_path)
    existing = pd.read_csv(rules_path) if rules_path.exists() else pd.DataFrame()
    existing = existing.drop(columns=['source_station_conditions', 'source_station_coverage',
                                      'rule_saved_at_utc'], errors='ignore')
    if rows and not existing.empty:
        configured_scales = {
            int(vars_id): scale for vars_id, scale in
            results.get('source_vars_time_scales', {}).items()
        }
        for row in rows:
            variable = row['canonical_variable']
            matching = existing.loc[
                (existing['network_id'].astype(int) == int(results['network_id'])) &
                (existing['canonical_variable'] == variable)
            ]
            if matching.empty:
                continue
            previous = matching.iloc[-1]
            preserved_ids = sorted(int(value) for value in json.loads(
                previous.get('source_vars_ids') or '[]'))
            if not preserved_ids:
                continue
            manual_ids = {
                int(value) for value in manual_source_ids.get(variable, [])}
            has_selection_evidence = (
                'recent_source_vars_ids' in previous.index and
                'candidate_vars_ids' in previous.index and
                pd.notna(previous.get('recent_source_vars_ids')) and
                pd.notna(previous.get('candidate_vars_ids'))
            )
            if has_selection_evidence:
                previous_recent_ids = {
                    int(value) for value in json.loads(
                        previous.get('recent_source_vars_ids') or '[]')}
                previous_candidate_ids = {
                    int(value) for value in json.loads(
                        previous.get('candidate_vars_ids') or '[]')}
                previous_manual_ids = (
                    set(preserved_ids) - previous_recent_ids)
                # A sole candidate can be saved automatically even when it has no
                # recent observations; do not misclassify it as a manual choice.
                if (len(previous_candidate_ids) == 1 and
                        set(preserved_ids) == previous_candidate_ids):
                    previous_manual_ids = set()
                # Manual IDs can also qualify as recent. Retain that information
                # when the current registry still records the same selection.
                previous_manual_ids |= manual_ids & set(preserved_ids)
                if manual_ids != previous_manual_ids:
                    continue
            elif manual_ids - set(preserved_ids):
                # Legacy rules do not contain enough evidence to identify past
                # manual choices. Preserve them unless the registry adds a new ID.
                continue
            previous_scales = json.loads(
                previous.get('source_vars_time_scales') or '{}')
            row['source_vars_ids'] = json.dumps(preserved_ids)
            row['source_vars_time_scales'] = json.dumps({
                str(vars_id): configured_scales.get(
                    vars_id, previous_scales.get(str(vars_id)))
                for vars_id in preserved_ids
                if (vars_id in configured_scales or
                    str(vars_id) in previous_scales)
            }, sort_keys=True)
            row['candidate_vars_ids'] = json.dumps(sorted(
                set(json.loads(row.get('candidate_vars_ids', '[]'))) |
                set(preserved_ids)))
    if 'candidate_vars_ids' not in existing.columns and not existing.empty:
        def candidate_ids_for_existing(row):
            variable = row['canonical_variable']
            if (int(float(row['network_id'])) == int(results['network_id']) and
                    variable in results['candidate_ids']):
                return sorted(
                    set(results['candidate_ids'][variable]) |
                    set(results.get('excluded_candidate_ids', {}).get(variable, [])))
            return sorted(
                set(json.loads(row.get('source_vars_ids', '[]'))) |
                set(json.loads(row.get('excluded_source_vars_ids', '[]'))))

        existing['candidate_vars_ids'] = existing.apply(
            lambda row: json.dumps(candidate_ids_for_existing(row)), axis=1)
    existing = existing.drop(columns=['excluded_source_vars_ids'], errors='ignore')
    if not rows:
        if rules_path.exists():
            existing = _order_rule_columns(existing)
            existing.to_csv(rules_path, index=False)
            if rules_path.parent.name.startswith('network_'):
                save_source_selection_summary(rules_path.parent.parent)
        return existing
    updates = pd.DataFrame(rows)
    if not existing.empty:
        keys = pd.MultiIndex.from_frame(updates[['network_id', 'canonical_variable']])
        old_keys = pd.MultiIndex.from_frame(existing[['network_id', 'canonical_variable']])
        existing = existing.loc[~old_keys.isin(keys)]
    combined = pd.concat([existing, updates], ignore_index=True).sort_values(
        ['network_id', 'canonical_variable']).reset_index(drop=True)
    combined = _order_rule_columns(combined)
    updates = _order_rule_columns(updates)
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(rules_path, index=False)
    # Preserve the final choices alongside this run's figures and review readouts.
    output_prefix = results.get('output_prefix', f"net{int(results['network_id'])}_")
    updates.to_csv(
        Path(results['run_dir']) / f'{output_prefix}final_variable_rules.csv',
        index=False,
    )
    if rules_path.parent.name.startswith('network_'):
        save_source_selection_summary(rules_path.parent.parent)
    return combined
