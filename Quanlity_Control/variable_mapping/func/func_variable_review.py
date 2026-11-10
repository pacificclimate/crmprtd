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
    CANONICAL_RULES, CANONICAL_VARIABLES, apply_canonical_rule,
    fetch_candidate_observations, select_candidate_stations,
)


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
    adjacent = ['source_vars_ids', 'recent_source_vars_ids',
                'recent_source_latest_observations']
    columns = [name for name in frame.columns if name not in adjacent]
    if 'source_vars_ids' not in frame.columns:
        return frame
    position = frame.columns.get_loc('source_vars_ids')
    columns[position:position] = [name for name in adjacent if name in frame.columns]
    return frame.loc[:, columns]


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


def _plot_variable(clean, variable, time_pdf, cdf_pdf):
    """One page per station in each report, preserving readable figure sizes."""
    if clean.empty:
        for pdf in (time_pdf, cdf_pdf):
            _notice(pdf, variable, 'No plausible data for the selected plot stations.')
        return
    ylabel = {'celsius': 'Temperature (°C)', 'mm': 'Amount (mm)',
              'cm': 'Amount (cm)'}[CANONICAL_RULES[variable].unit]
    positive_only = variable in {'precipitation_amount', 'snowfall_amount'}
    for station_id, frame in clean.groupby('station_id'):
        title = f"{variable} — {frame['station_name'].iloc[0]} (station {station_id})"
        for mode, pdf in [('time_series', time_pdf), ('cdf', cdf_pdf)]:
            fig, ax = plt.subplots(figsize=(14, 5))
            any_values = False
            for (vid, name), data in frame.groupby(['vars_id', 'net_var_name']):
                label = f'{vid} — {name}'
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
                         auto_keep_from='2026-01-01'):
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
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = Path(mkdtemp(prefix='.review_staging_', dir=output_dir)).resolve()
    latest_dir = (output_dir / 'latest_review').resolve()
    results = {'run_dir': str(run_dir), 'network_id': int(network_id),
               'candidate_ids': {}, 'rules': [], 'status': []}
    reviews, qc_tables, condition_tables = [], [], []
    mappings = candidate_mappings.loc[candidate_mappings.network_id == network_id]
    with PdfPages(run_dir / 'time_series.pdf') as time_pdf, PdfPages(run_dir / 'cdf.pdf') as cdf_pdf:
        for variable in variables:
            print(f'Reviewing {variable}...', flush=True)
            candidates = mappings.loc[mappings.canonical_variable == variable].drop_duplicates('vars_id').copy()
            candidate_ids = sorted(int(value) for value in candidates.vars_id)
            results['candidate_ids'][variable] = candidate_ids
            status = dict(canonical_variable=variable, status='ok', eligible_station_count=0,
                          source_station_count=0, plot_station_ids=[])
            results['status'].append(status)
            if candidates.empty:
                status['status'] = 'no_candidates'
            else:
                eligible = select_candidate_stations(engine, candidate_ids, network_id=network_id, limit=None)
                status['eligible_station_count'] = len(eligible)
                if eligible.empty:
                    status['status'] = 'no_matching_stations'
            if status['status'] != 'ok':
                for pdf in (time_pdf, cdf_pdf):
                    _notice(pdf, variable, status['status'].replace('_', ' '))
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
            latest = {str(int(row.vars_id)): pd.Timestamp(row.latest_observation_from_cutoff).isoformat()
                      for row in recent.itertuples(index=False)}
            candidate_review = candidates.merge(coverage, on='vars_id', how='left', validate='one_to_one')
            candidate_review['decision'] = candidate_review.vars_id.map(
                lambda vid: 'automatic keep' if vid in auto_ids else 'manual decision')
            candidate_review['source_checked_at_utc'] = checked_at
            reviews.append(format_candidate_review(candidate_review))
            condition_tables.append(conditions.assign(network_id=network_id, canonical_variable=variable))
            results['rules'].append(dict(
                network_id=int(network_id), canonical_variable=variable,
                source_vars_ids=json.dumps(auto_ids), auto_keep_from=auto_keep_from,
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
            _plot_variable(clean, variable, time_pdf, cdf_pdf)

    for name, tables, columns in [
        ('candidate_review', reviews, ['canonical_variable', 'vars_id', 'total_station_count', 'recent_non_null_station_count']),
        ('qc_summary', qc_tables, ['canonical_variable', 'vars_id']),
        ('station_conditions', condition_tables, ['canonical_variable', 'vars_id', 'station_id']),
    ]:
        frame = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame(columns=columns)
        keys = [key for key in ['canonical_variable', 'vars_id', 'station_id'] if key in frame]
        frame.sort_values(keys).to_csv(run_dir / f'{name}.csv', index=False)
    pd.DataFrame(results['status']).to_csv(run_dir / 'run_summary.csv', index=False)
    results['run_dir'] = str(latest_dir)
    (run_dir / 'review_results.json').write_text(json.dumps(results, indent=2) + '\n')
    run_dir = _promote_latest_review(run_dir, output_dir)
    print(f'Review complete: {run_dir}', flush=True)
    return results


def save_review_rules(results, manual_source_ids, rules_path):
    """Apply manual additions to completed reviews and upsert rules without queries.

    Empty selections leave existing rules unchanged. All manual IDs are validated
    before any CSV write. Legacy detailed-condition/save-time columns are removed.
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
        chosen = sorted(set(json.loads(row['recent_source_vars_ids'])) |
                        {int(vid) for vid in manual_source_ids.get(variable, [])})
        if not chosen:
            print(f'No sources selected for {variable}; existing rule left unchanged.')
            continue
        row['source_vars_ids'] = json.dumps(chosen)
        rows.append(row)
    rules_path = Path(rules_path)
    existing = pd.read_csv(rules_path) if rules_path.exists() else pd.DataFrame()
    existing = existing.drop(columns=['source_station_conditions', 'source_station_coverage',
                                      'rule_saved_at_utc'], errors='ignore')
    if not rows:
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
    updates.to_csv(Path(results['run_dir']) / 'final_rules.csv', index=False)
    return combined
