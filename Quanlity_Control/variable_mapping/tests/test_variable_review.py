import json
from pathlib import Path
import re
import sys
from unittest.mock import patch

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'func'))
import func_variable_mapping as mapping
import func_variable_review as review


def registry():
    return pd.DataFrame([
        dict(network_id=2, canonical_variable=name, vars_id=vid,
             net_var_name=f'candidate_{vid}', daily_aggregation='mean',
             priority=1, mapping_status='candidate',
             network_station_count=25 if vid == 101 else 12)
        for name in review.CANONICAL_VARIABLES for vid in (101, 102)
    ])


def fake_observations(engine, ids, stations):
    return pd.DataFrame([
        dict(station_id=station, station_name=f'Station {station}', vars_id=vid,
             net_var_name=f'candidate_{vid}', obs_time=pd.Timestamp('2026-02-01'), datum=1.0)
        for station in stations for vid in ids
    ])


def fake_recent(query, engine, params):
    assert len(params['station_ids']) <= 20
    assert set(params['station_ids']) <= set(range(1, 26))
    assert 's.station_id IN' in str(query)
    return pd.DataFrame([
        dict(station_id=station, vars_id=vid,
             latest_observation_from_cutoff=pd.Timestamp('2026-02-01') if vid == 101 else pd.NaT)
        for station in params['station_ids'] for vid in params['vars_ids']
    ])


def test_add_network_station_counts_keeps_zero_and_excluded_candidates():
    candidates = pd.DataFrame([
        dict(network_id=11, vars_id=501, mapping_status='needs_review'),
        dict(network_id=11, vars_id=1268, mapping_status='excluded'),
    ])
    network_counts = pd.DataFrame([
        dict(vars_id=501, net_var_name='Rainmm', station_count=43,
             station_ids='1, 2', station_names='One; Two'),
    ])

    with patch.object(
            mapping, 'summarize_variable_station_presence',
            return_value=network_counts):
        enriched = mapping.add_network_station_counts(
            None, candidates, network_id=11)

    assert enriched.network_station_count.tolist() == [43, 0]
    assert enriched.mapping_status.tolist() == ['needs_review', 'excluded']


def test_candidate_registry_loads_legacy_and_saves_network_station_count(tmp_path):
    path = tmp_path / 'net11_candidate_mappings.csv'
    legacy = pd.DataFrame([dict(
        network_id=11, vars_id=501, net_var_name='Rainmm',
        canonical_variable='precipitation_amount', daily_aggregation='sum',
        priority=1, source_family='network11_auto',
        mapping_status='needs_review',
    )])
    legacy.to_csv(path, index=False)

    loaded = mapping.load_candidate_mappings(path)
    assert 'network_station_count' in loaded
    assert loaded.network_station_count.isna().all()
    assert 'source_time_scale' in loaded
    assert loaded.source_time_scale.isna().all()
    assert 'daily_boundary_hour' not in loaded
    assert 'daily_time_basis' not in loaded
    assert 'daily_processing_status' not in loaded

    loaded['network_station_count'] = 43
    loaded['source_time_scale'] = 'hourly'
    mapping.save_candidate_mappings(11, loaded, path)
    saved = pd.read_csv(path)
    assert saved.network_station_count.tolist() == [43]
    assert saved.source_time_scale.tolist() == ['hourly']


def test_daily_processing_uses_as_is_for_every_daily_source():
    mappings = pd.DataFrame([
        dict(vars_id=429, canonical_variable='precipitation_amount',
             source_time_scale='daily', mapping_status='needs_review'),
        dict(vars_id=726, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=732, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=442, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=440, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=443, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=501, canonical_variable='precipitation_amount',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=503, canonical_variable='air_temperature',
             source_time_scale='hourly', mapping_status='needs_review'),
        dict(vars_id=504, canonical_variable='daily_min_temperature',
             source_time_scale='daily', mapping_status='needs_review'),
        dict(vars_id=505, canonical_variable='daily_max_temperature',
             source_time_scale='daily', mapping_status='needs_review'),
        dict(vars_id=506, canonical_variable='snowfall_amount',
             source_time_scale='daily', mapping_status='needs_review'),
        dict(vars_id=507, canonical_variable='snow_depth',
             source_time_scale='daily', mapping_status='needs_review'),
        dict(vars_id=999, canonical_variable='precipitation_amount',
             source_time_scale=pd.NA, mapping_status='excluded'),
    ])
    metadata = pd.DataFrame([
        dict(vars_id=429, net_var_name='ONE_DAY_PRECIPITATION',
             cell_method='time: sum', long_description='Daily precipitation'),
        dict(vars_id=726, net_var_name='pcpn_amt_pst1hr',
             cell_method='time: sum (interval: 1 hour)'),
        dict(vars_id=732, net_var_name='pcpn_amt_pst24hrs',
             cell_method='time: sum (interval: 24 hour)'),
        dict(vars_id=442, net_var_name='HOURLY_PRECIPITATION',
             cell_method='t: sum within days interval: daily'),
        dict(vars_id=440, net_var_name='PRECIPITATION_GAUGE_TOTAL',
             cell_method='t: sum over days interval: irregular'),
        dict(vars_id=443, net_var_name='PRECIP_DETECTOR_RATIO',
             cell_method='time: mean'),
        dict(vars_id=501, net_var_name='Rainmm', cell_method='time: sum'),
        dict(vars_id=503, net_var_name='AirTemp', cell_method='time: point'),
        dict(vars_id=504, net_var_name='DailyMin', cell_method='time: minimum'),
        dict(vars_id=505, net_var_name='DailyMax', cell_method='time: maximum'),
        dict(vars_id=506, net_var_name='DailySnow', cell_method='time: sum'),
        dict(vars_id=507, net_var_name='DailyDepth', cell_method='time: point'),
        dict(vars_id=999, net_var_name='Rain', cell_method='time: sum'),
    ])

    result = mapping.add_candidate_daily_processing(mappings, metadata)
    result = result.set_index('vars_id')

    assert result.daily_aggregation.to_dict() == {
        429: 'as_is',
        726: 'sum',
        732: 'fixed_hour_previous_day',
        442: 'last',
        440: 'difference',
        443: 'not_applicable',
        501: 'sum',
        503: 'mean',
        504: 'as_is',
        505: 'as_is',
        506: 'as_is',
        507: 'as_is',
        999: 'sum',
    }
    assert 'daily_boundary_hour' not in result
    assert 'daily_time_basis' not in result
    assert 'daily_processing_status' not in result
    assert result.loc[443, 'mapping_status'] == 'excluded'


def test_reviewed_daily_aggregation_override_is_supported():
    mappings = pd.DataFrame([dict(
        vars_id=732, canonical_variable='precipitation_amount',
        source_time_scale='hourly', mapping_status='needs_review')])
    metadata = pd.DataFrame([dict(
        vars_id=732, net_var_name='pcpn_amt_pst24hrs',
        cell_method='time: sum (interval: 24 hour)')])
    overrides = {732: {'daily_aggregation': 'sum'}}

    result = mapping.add_candidate_daily_processing(
        mappings, metadata, overrides=overrides).iloc[0]

    assert result.daily_aggregation == 'sum'
    assert 'daily_boundary_hour' not in result
    assert 'daily_time_basis' not in result
    assert 'daily_processing_status' not in result


@pytest.mark.parametrize(('timestamps', 'metadata', 'history_frequency', 'expected'), [
    (pd.date_range('2026-01-01', periods=10, freq='h'),
     'rolling precipitation interval: 24 hour', None, 'hourly'),
    (pd.date_range('2026-01-01', periods=10, freq='30min'), '', None, 'hourly'),
    (pd.date_range('2026-01-01', periods=10, freq='D'), '', None, 'daily'),
    ([pd.Timestamp('2026-01-01')], 'Hourly precipitation', None, 'hourly'),
    ([pd.Timestamp('2026-01-01')], '', '1-daily', 'daily'),
    ([pd.Timestamp('2026-01-01')], 'interval: 24 hour', None, None),
])
def test_classify_source_time_scale_hybrid(
        timestamps, metadata, history_frequency, expected):
    assert mapping.classify_source_time_scale(
        timestamps, metadata, history_frequency) == expected


def test_add_candidate_time_scales_excludes_zero_station_candidates_without_sampling():
    candidates = pd.DataFrame([
        dict(vars_id=501, mapping_status='candidate', network_station_count=43),
        dict(vars_id=529, mapping_status='needs_review', network_station_count=0),
        dict(vars_id=1266, mapping_status='excluded', network_station_count=0),
    ])
    metadata = pd.DataFrame([
        dict(vars_id=501, net_var_name='Rainmm', standard_name=pd.NA),
        dict(vars_id=529, net_var_name='DailyRain', standard_name=pd.NA),
        dict(vars_id=1266, net_var_name='Rainmm_raw', standard_name=pd.NA),
    ])
    evidence = (pd.date_range('2026-01-01', periods=20, freq='h'), '1-hourly')

    with patch.object(
            mapping, '_sample_source_time_scale_evidence',
            return_value=evidence) as sample:
        enriched = mapping.add_candidate_time_scales(
            None, candidates, metadata, network_id=11)

    saved = enriched.set_index('vars_id')
    assert saved.loc[501, 'source_time_scale'] == 'hourly'
    assert pd.isna(saved.loc[529, 'source_time_scale'])
    assert pd.isna(saved.loc[1266, 'source_time_scale'])
    assert saved.loc[529, 'mapping_status'] == 'excluded'
    assert saved.loc[1266, 'mapping_status'] == 'excluded'
    sample.assert_called_once_with(None, 501, 300)


def test_add_candidate_time_scales_rejects_unresolved_and_bad_overrides():
    candidates = pd.DataFrame([dict(vars_id=501, mapping_status='candidate')])
    metadata = pd.DataFrame([dict(vars_id=501, net_var_name='Rain')])
    empty_evidence = (pd.DatetimeIndex([]), None)

    with patch.object(
            mapping, '_sample_source_time_scale_evidence',
            return_value=empty_evidence):
        with pytest.raises(ValueError, match=r'Unresolved.*501'):
            mapping.add_candidate_time_scales(
                None, candidates, metadata, network_id=11)

    with pytest.raises(ValueError, match="hourly.*daily"):
        mapping.add_candidate_time_scales(
            None, candidates, metadata, network_id=11,
            overrides={501: 'monthly'})
    with pytest.raises(ValueError, match=r'not candidates.*999'):
        mapping.add_candidate_time_scales(
            None, candidates, metadata, network_id=11,
            overrides={999: 'hourly'})


def test_candidate_source_time_scales_prefers_saved_then_legacy():
    candidates = pd.DataFrame([
        dict(vars_id=501, mapping_status='candidate', source_time_scale='daily'),
        dict(vars_id=503, mapping_status='needs_review', source_time_scale=pd.NA),
        dict(vars_id=999, mapping_status='excluded', source_time_scale=pd.NA),
    ])

    assert review.candidate_source_time_scales(candidates, 11) == {
        501: 'daily', 503: 'hourly'}


def test_candidate_source_time_scales_errors_without_saved_or_legacy():
    candidates = pd.DataFrame([
        dict(vars_id=9001, mapping_status='candidate', source_time_scale=pd.NA),
    ])
    with pytest.raises(ValueError, match=r'Missing daily/hourly labels.*9001'):
        review.candidate_source_time_scales(candidates, 77)


def run_batch(tmp_path, eligible=None, observations=fake_observations, network_id=2,
              source_vars_time_scales=None):
    if eligible is None:
        eligible = pd.DataFrame({'station_id': range(1, 26)})
    with patch.object(review, 'select_candidate_stations', return_value=eligible) as select, \
         patch.object(review, 'fetch_candidate_observations', side_effect=observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent) as read:
        results = review.run_variable_reviews(
            None, registry(), tmp_path, network_id=network_id, plot_station_limit=1,
            source_station_limit=20, random_seed=42,
            source_vars_time_scales=source_vars_time_scales,
        )
        assert select.call_count == (12 if eligible.empty else 6)
        if not eligible.empty:
            assert read.call_count == 6
    return results


def test_successful_run_keeps_only_latest_result_for_each_network(tmp_path):
    network_dir = tmp_path / 'network_2'
    other_network = tmp_path / 'network_20'
    other_network.mkdir()
    unrelated = other_network / 'latest_review'
    unrelated.mkdir()

    first = Path(run_batch(network_dir)['run_dir'])
    assert first == network_dir / 'latest_review'
    marker = first / 'old-marker'
    marker.write_text('old')
    second = Path(run_batch(network_dir)['run_dir'])

    assert second == first
    assert not marker.exists()
    assert (second / 'net2_review_results.json').is_file()
    assert unrelated.is_dir()


def test_failed_run_preserves_previous_latest_review(tmp_path):
    network_dir = tmp_path / 'network_2'
    latest = Path(run_batch(network_dir)['run_dir'])
    marker = latest / 'previous-success'
    marker.write_text('keep')

    with patch.object(review, '_plot_variable', side_effect=RuntimeError('plot failed')):
        with pytest.raises(RuntimeError, match='plot failed'):
            run_batch(network_dir)

    assert marker.read_text() == 'keep'
    assert not list(network_dir.glob('.review_backup_*'))


def test_one_run_six_variables_and_two_pdfs(tmp_path):
    results = run_batch(tmp_path)
    folder = Path(results['run_dir'])
    assert len(results['rules']) == 6
    for filename in ['net2_time_series.pdf', 'net2_cdf.pdf']:
        data = (folder / filename).read_bytes()
        assert len(re.findall(rb'/Type /Page\b', data)) == 6
    readout = pd.read_csv(folder / 'net2_candidate_review.csv')
    assert len(readout) == 12
    assert 'total_station_count' not in readout
    assert 'mapping_status' not in readout
    assert readout.columns[-1] == 'priority'
    assert readout.columns[readout.columns.get_loc('daily_aggregation') + 1] == 'decision' 
    assert set(readout.loc[readout.vars_id == 101, 'recent_non_null_station_count']) == {20}
    assert set(readout.loc[readout.vars_id == 101, 'network_station_count']) == {25}
    assert (folder / 'net2_qc_summary.csv').is_file()
    assert len(pd.read_csv(folder / 'net2_station_conditions.csv')) == 240
    restored = json.loads((folder / 'net2_review_results.json').read_text())
    assert restored['rules'] == results['rules']
    assert all(len(json.loads(row['source_station_ids'])) == 20 for row in results['rules'])
    assert {row['station_selection_method'] for row in results['status']} == {
        'all_candidates'}
    run_summary = pd.read_csv(folder / 'net2_run_summary.csv')
    assert set(run_summary.station_selection_method) == {'all_candidates'}
    with patch.object(review.pd, 'read_sql', side_effect=AssertionError('Save queried DB')):
        final = review.save_review_rules(restored, {'daily_min_temperature': [102]}, tmp_path / 'rules.csv')
    assert len(final) == 6
    chosen = final.set_index('canonical_variable').loc['daily_min_temperature']
    assert json.loads(chosen.source_vars_ids) == [101, 102]
    assert not {'rule_saved_at_utc', 'source_station_conditions', 'source_station_coverage'} & set(final)
    expected = ['source_vars_ids', 'source_vars_time_scales', 'candidate_vars_ids',
                'recent_source_vars_ids',
                'recent_source_latest_observations']
    start = final.columns.get_loc('source_vars_ids')
    assert final.columns[start:start + 5].tolist() == expected
    run_final = pd.read_csv(folder / 'net2_final_variable_rules.csv')
    start = run_final.columns.get_loc('source_vars_ids')
    assert run_final.columns[start:start + 5].tolist() == expected


def test_empty_strict_selection_falls_back_to_any_candidate(tmp_path):
    strict = pd.DataFrame(columns=['station_id'])
    fallback = pd.DataFrame({'station_id': [1, 2]})
    with patch.object(review, 'select_candidate_stations',
                      side_effect=[strict, fallback]), \
         patch.object(review, 'fetch_candidate_observations',
                      side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent):
        results = review.run_variable_reviews(
            None, registry(), tmp_path, network_id=2,
            variables=['air_temperature'], plot_station_limit=1,
            source_station_limit=2, random_seed=42,
        )

    status = results['status'][0]
    assert status['status'] == 'ok'
    assert status['eligible_station_count'] == 2
    assert status['station_selection_method'] == 'any_candidate_fallback'
    assert len(results['rules']) == 1


def test_candidate_station_match_mode_is_validated():
    with pytest.raises(ValueError, match="match must be 'all' or 'any'"):
        review.select_candidate_stations(None, [101], match='neither')


def test_time_series_pages_share_variable_time_range():
    clean = pd.DataFrame([
        dict(station_id=1, station_name='Early', vars_id=101,
             net_var_name='candidate_101', obs_time=pd.Timestamp('2020-01-01'), datum=1.0),
        dict(station_id=1, station_name='Early', vars_id=101,
             net_var_name='candidate_101', obs_time=pd.Timestamp('2020-02-01'), datum=2.0),
        dict(station_id=2, station_name='Late', vars_id=101,
             net_var_name='candidate_101', obs_time=pd.Timestamp('2022-01-01'), datum=3.0),
        dict(station_id=2, station_name='Late', vars_id=101,
             net_var_name='candidate_101', obs_time=pd.Timestamp('2022-02-01'), datum=4.0),
    ])

    class RecordingPdf:
        def __init__(self):
            self.xlimits = []
            self.legend_labels = []

        def savefig(self, figure, **kwargs):
            self.xlimits.append(figure.axes[0].get_xlim())
            legend = figure.axes[0].get_legend()
            self.legend_labels.append(
                [text.get_text() for text in legend.get_texts()] if legend else [])

    time_pdf, cdf_pdf = RecordingPdf(), RecordingPdf()
    review._plot_variable(
        clean, 'air_temperature', time_pdf, cdf_pdf,
        source_vars_time_scales={101: 'hourly'})

    assert len(time_pdf.xlimits) == 2
    assert time_pdf.xlimits[0] == pytest.approx(time_pdf.xlimits[1])
    assert time_pdf.legend_labels[0] == ['101 — candidate_101 (hourly)']


def test_excluded_candidates_are_recorded_but_never_reviewed(tmp_path):
    mappings = pd.DataFrame([
        dict(network_id=2, canonical_variable='air_temperature', vars_id=101,
             net_var_name='active', daily_aggregation='mean', priority=1,
             mapping_status='needs_review', network_station_count=1),
        dict(network_id=2, canonical_variable='air_temperature', vars_id=999,
             net_var_name='excluded', daily_aggregation='mean', priority=2,
             mapping_status='excluded', network_station_count=0),
    ])

    def select_only_active(engine, ids, **kwargs):
        assert list(ids) == [101]
        return pd.DataFrame({'station_id': [1]})

    def fetch_only_active(engine, ids, stations):
        assert list(ids) == [101]
        return fake_observations(engine, ids, stations)

    def recent_only_active(query, engine, params):
        assert params['vars_ids'] == [101]
        return fake_recent(query, engine, params)

    with patch.object(review, 'select_candidate_stations',
                      side_effect=select_only_active), \
         patch.object(review, 'fetch_candidate_observations',
                      side_effect=fetch_only_active), \
         patch.object(review.pd, 'read_sql', side_effect=recent_only_active):
        results = review.run_variable_reviews(
            None, mappings, tmp_path, network_id=2,
            variables=['air_temperature'], plot_station_limit=1,
            source_station_limit=1, random_seed=42,
        )

    assert results['candidate_ids']['air_temperature'] == [101]
    rule = results['rules'][0]
    assert json.loads(rule['source_vars_ids']) == [101]
    assert json.loads(rule['candidate_vars_ids']) == [101, 999]
    assert results['excluded_candidate_ids']['air_temperature'] == [999]


def test_recent_candidates_are_automatically_kept_without_processing_status(tmp_path):
    mappings = pd.DataFrame([
        dict(network_id=2, canonical_variable='precipitation_amount', vars_id=101,
             net_var_name='rolling_24h', daily_aggregation='fixed_hour_previous_day',
             priority=1,
             mapping_status='needs_review', network_station_count=1),
        dict(network_id=2, canonical_variable='precipitation_amount', vars_id=102,
             net_var_name='daily_amount', daily_aggregation='as_is', priority=2,
             mapping_status='needs_review', network_station_count=1),
    ])

    def recent_for_both(query, engine, params):
        return pd.DataFrame([
            dict(station_id=1, vars_id=vid,
                 latest_observation_from_cutoff=pd.Timestamp('2026-02-01'))
            for vid in params['vars_ids']
        ])

    with patch.object(review, 'select_candidate_stations',
                      return_value=pd.DataFrame({'station_id': [1]})), \
         patch.object(review, 'fetch_candidate_observations',
                      side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=recent_for_both):
        results = review.run_variable_reviews(
            None, mappings, tmp_path, network_id=2,
            variables=['precipitation_amount'], plot_station_limit=1,
            source_station_limit=1, random_seed=42,
        )

    rule = results['rules'][0]
    assert json.loads(rule['recent_source_vars_ids']) == [101, 102]
    assert json.loads(rule['source_vars_ids']) == [101, 102]
    assert 'daily_processing_status' not in results
    readout = pd.read_csv(
        Path(results['run_dir']) / 'net2_candidate_review.csv').set_index('vars_id')
    assert readout.loc[101, 'decision'] == 'automatic keep'
    assert readout.loc[102, 'decision'] == 'automatic keep'

    saved = review.save_review_rules(results, {}, tmp_path / 'rules.csv')
    columns = saved.columns.tolist()
    start = columns.index('source_vars_ids')
    assert columns[start:start + 5] == [
        'source_vars_ids', 'source_vars_time_scales', 'candidate_vars_ids',
        'recent_source_vars_ids', 'recent_source_latest_observations',
    ]
    assert 'excluded_source_vars_ids' not in columns


def test_single_candidate_is_saved_even_without_recent_data(tmp_path):
    mappings = pd.DataFrame([dict(
        network_id=19, canonical_variable='precipitation_amount', vars_id=837,
        net_var_name='only_candidate', daily_aggregation='sum', priority=1,
        mapping_status='candidate', network_station_count=1,
    )])
    eligible = pd.DataFrame({'station_id': [1]})

    def no_recent(query, engine, params):
        return pd.DataFrame([dict(
            station_id=1, vars_id=837, latest_observation_from_cutoff=pd.NaT,
        )])

    with patch.object(review, 'select_candidate_stations', return_value=eligible), \
         patch.object(review, 'fetch_candidate_observations', side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=no_recent):
        results = review.run_variable_reviews(
            None, mappings, tmp_path, network_id=19,
            variables=['precipitation_amount'], plot_station_limit=1,
            source_station_limit=1, random_seed=42,
        )

    saved = review.save_review_rules(
        results, {}, tmp_path / 'net19_final_variable_rules.csv')
    row = saved.iloc[0]
    assert json.loads(row.source_vars_ids) == [837]
    assert json.loads(row.candidate_vars_ids) == [837]


def test_single_candidate_without_matching_station_is_still_saved(tmp_path):
    mappings = pd.DataFrame([dict(
        network_id=19, canonical_variable='air_temperature', vars_id=546,
        net_var_name='only_candidate', daily_aggregation='mean', priority=1,
        mapping_status='candidate', network_station_count=0,
    )])
    with patch.object(review, 'select_candidate_stations',
                      return_value=pd.DataFrame(columns=['station_id'])):
        results = review.run_variable_reviews(
            None, mappings, tmp_path, network_id=19,
            variables=['air_temperature'], plot_station_limit=1,
            source_station_limit=1, random_seed=42,
        )

    saved = review.save_review_rules(
        results, {}, tmp_path / 'net19_final_variable_rules.csv')
    assert json.loads(saved.iloc[0].source_vars_ids) == [546]
    assert json.loads(saved.iloc[0].candidate_vars_ids) == [546]


def test_source_time_scales_are_saved_for_selected_sources(tmp_path):
    results = run_batch(
        tmp_path, source_vars_time_scales={101: 'daily', 102: 'hourly'})

    saved = review.save_review_rules(
        results, {'air_temperature': [102]}, tmp_path / 'rules.csv')
    row = saved.loc[saved.canonical_variable == 'air_temperature'].iloc[0]

    assert json.loads(row.source_vars_time_scales) == {
        '101': 'daily', '102': 'hourly'}


def test_configured_time_scales_must_cover_every_active_candidate(tmp_path):
    with pytest.raises(ValueError, match=r'active candidate vars_ids: \[102\]'):
        run_batch(tmp_path, source_vars_time_scales={101: 'daily'})


def test_batch_enriches_legacy_candidate_counts_once(tmp_path):
    mappings = registry().drop(columns='network_station_count')
    enriched = mappings.assign(network_station_count=7)
    eligible = pd.DataFrame({'station_id': [1, 2]})
    calls = 0

    def add_counts_once(engine, candidates, network_id):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise AssertionError('station counts queried more than once')
        return enriched

    with patch.object(
            review, 'add_network_station_counts', side_effect=add_counts_once), \
         patch.object(review, 'select_candidate_stations', return_value=eligible), \
         patch.object(review, 'fetch_candidate_observations',
                      side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent):
        results = review.run_variable_reviews(
            None, mappings, tmp_path, network_id=2,
            variables=['air_temperature'], plot_station_limit=1,
            source_station_limit=2, random_seed=42)

    review_table = pd.read_csv(
        Path(results['run_dir']) / 'net2_candidate_review.csv')
    assert review_table.network_station_count.tolist() == [7, 7]


def test_batch_reuses_complete_network_station_counts(tmp_path):
    eligible = pd.DataFrame({'station_id': [1, 2]})
    with patch.object(
            review, 'add_network_station_counts',
            side_effect=AssertionError('unexpected station-count query')), \
         patch.object(review, 'select_candidate_stations', return_value=eligible), \
         patch.object(review, 'fetch_candidate_observations',
                      side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent):
        results = review.run_variable_reviews(
            None, registry(), tmp_path, network_id=2,
            variables=['air_temperature'], plot_station_limit=1,
            source_station_limit=2, random_seed=42)

    review_table = pd.read_csv(
        Path(results['run_dir']) / 'net2_candidate_review.csv')
    assert review_table.network_station_count.tolist() == [25, 12]


def test_every_active_network_candidate_has_a_configured_time_scale():
    networks_dir = Path(__file__).resolve().parents[1] / 'networks'
    for registry_path in networks_dir.glob(
            'network_*/net*_candidate_mappings.csv'):
        registry_frame = pd.read_csv(registry_path)
        network_id = int(registry_path.parent.name.removeprefix('network_'))
        configured = review.candidate_source_time_scales(
            registry_frame, network_id)
        active_ids = set(registry_frame.loc[
            ~registry_frame.mapping_status.eq('excluded'), 'vars_id'].astype(int))
        assert active_ids <= set(configured), (
            network_id, active_ids - set(configured))


def test_every_persisted_source_has_a_configured_time_scale():
    networks_dir = Path(__file__).resolve().parents[1] / 'networks'
    for rules_path in networks_dir.glob(
            'network_*/net*_final_variable_rules.csv'):
        rules = pd.read_csv(rules_path)
        network_id = int(rules.network_id.iloc[0])
        candidate_path = (
            rules_path.parent / f'net{network_id}_candidate_mappings.csv')
        configured = review.candidate_source_time_scales(
            pd.read_csv(candidate_path), network_id)
        source_ids = {
            int(vars_id)
            for value in rules.source_vars_ids
            for vars_id in json.loads(value)
        }
        assert source_ids <= set(configured), (network_id, source_ids - set(configured))


def test_cross_network_source_selection_summary(tmp_path):
    networks = tmp_path / 'networks'
    network_2 = networks / 'network_2'
    network_5 = networks / 'network_5'
    network_2.mkdir(parents=True)
    network_5.mkdir(parents=True)
    pd.DataFrame([
        dict(network_id=2, canonical_variable='air_temperature',
             source_vars_ids='[434, 721]', recent_source_vars_ids='[721]',
             source_vars_time_scales='{"434": "daily", "721": "hourly"}',
             candidate_vars_ids='[434, 436, 721]', source_checked_at_utc='checked-2'),
    ]).to_csv(network_2 / 'net2_final_variable_rules.csv', index=False)
    pd.DataFrame([
        dict(network_id=5, canonical_variable='snow_depth',
             source_vars_ids='[468, 1331]', recent_source_vars_ids='[]',
             candidate_vars_ids='[468, 1331]', source_checked_at_utc='checked-5'),
        dict(network_id=5, canonical_variable='snowfall_amount',
             source_vars_ids='[467]', recent_source_vars_ids='[]',
             candidate_vars_ids='[467, 999]', source_checked_at_utc='checked-5'),
    ]).to_csv(network_5 / 'net5_final_variable_rules.csv', index=False)
    pd.DataFrame([
        dict(network_id=5, canonical_variable='snow_depth', vars_id=468,
             mapping_status='candidate'),
        dict(network_id=5, canonical_variable='snow_depth', vars_id=1331,
             mapping_status='needs_review'),
        dict(network_id=5, canonical_variable='snowfall_amount', vars_id=467,
             mapping_status='candidate'),
        dict(network_id=5, canonical_variable='snowfall_amount', vars_id=999,
             mapping_status='excluded'),
    ]).to_csv(network_5 / 'net5_candidate_mappings.csv', index=False)

    summary = review.save_source_selection_summary(networks)

    assert summary.network_id.tolist() == [2, 5, 5]
    first = summary.iloc[0]
    assert json.loads(first.automatically_recognized_source_vars_ids) == [721]
    assert json.loads(first.manually_saved_source_vars_ids) == [434]
    assert json.loads(first.source_vars_time_scales) == {
        '434': 'daily', '721': 'hourly'}
    second = summary.iloc[1]
    assert json.loads(second.automatically_recognized_source_vars_ids) == []
    assert json.loads(second.manually_saved_source_vars_ids) == [468, 1331]
    assert json.loads(second.single_candidate_saved_source_vars_ids) == []
    third = summary.iloc[2]
    assert json.loads(third.single_candidate_saved_source_vars_ids) == [467]
    assert json.loads(third.manually_saved_source_vars_ids) == []
    assert (networks / 'all_networks_source_vars_summary.csv').is_file()


def test_missing_stations_and_empty_plots_are_reported(tmp_path):
    results = run_batch(tmp_path, eligible=pd.DataFrame({'station_id': []}))
    assert not results['rules']
    assert {row['status'] for row in results['status']} == {'no_matching_stations'}
    def invalid(*args):
        frame = fake_observations(*args)
        frame['datum'] = float('nan')
        return frame
    results = run_batch(tmp_path, eligible=pd.DataFrame({'station_id': [1, 2]}), observations=invalid)
    assert len(results['rules']) == 6
    assert {row['status'] for row in results['status']} == {'no_plausible_plot_data'}
    assert all(row['source_station_count'] == 2 for row in results['rules'])


def test_manual_validation_and_preserve_existing_rules(tmp_path):
    results = run_batch(tmp_path)
    target = tmp_path / 'rules.csv'
    pd.DataFrame([dict(network_id=19, canonical_variable='air_temperature', source_vars_ids='[999]',
                       rule_saved_at_utc='old', source_station_conditions='old')]).to_csv(target,index=False)
    before = target.read_bytes()
    with pytest.raises(ValueError):
        review.save_review_rules(results, {'daily_min_temperature': [999]}, target)
    assert target.read_bytes() == before
    with pytest.raises(ValueError):
        review.save_review_rules(results, {'typo_variable': [101]}, target)
    saved = review.save_review_rules(results, {}, target)
    assert len(saved) == 7
    assert saved.loc[saved.network_id == 19, 'source_vars_ids'].iloc[0] == '[999]'


def test_no_recent_sources_preserves_existing_rule_until_manual_choice(tmp_path):
    results = run_batch(tmp_path)
    for row in results['rules']:
        row['recent_source_vars_ids'] = '[]'
        row['source_vars_ids'] = '[]'
        row['recent_source_latest_observations'] = '{}'
    target = tmp_path / 'rules.csv'
    pd.DataFrame([dict(network_id=2, canonical_variable='air_temperature',
                       source_vars_ids='[102]')]).to_csv(target, index=False)
    saved = review.save_review_rules(results, {}, target)
    assert saved.source_vars_ids.tolist() == ['[102]']
    assert json.loads(saved.candidate_vars_ids.iloc[0]) == [101, 102]
    assert 'candidate_vars_ids' in pd.read_csv(target).columns
    saved = review.save_review_rules(results, {'daily_min_temperature': [102]}, target)
    assert len(saved) == 2
    assert json.loads(saved.set_index('canonical_variable').loc[
        'daily_min_temperature', 'source_vars_ids']) == [102]


def test_rerun_preserves_existing_source_ids_without_manual_change(tmp_path):
    results = run_batch(tmp_path)
    target = tmp_path / 'rules.csv'
    pd.DataFrame([dict(
        network_id=2,
        canonical_variable='air_temperature',
        source_vars_ids='[102]',
        source_vars_time_scales='{"102": "daily"}',
    )]).to_csv(target, index=False)

    saved = review.save_review_rules(results, {}, target)

    rule = saved.set_index('canonical_variable').loc['air_temperature']
    assert json.loads(rule.source_vars_ids) == [102]
    assert json.loads(rule.source_vars_time_scales) == {'102': 'daily'}


def test_recorded_manual_id_does_not_expand_existing_selection(tmp_path):
    results = run_batch(tmp_path)
    target = tmp_path / 'rules.csv'
    pd.DataFrame([dict(
        network_id=2,
        canonical_variable='air_temperature',
        source_vars_ids='[102]',
        source_vars_time_scales='{"102": "daily"}',
        recent_source_vars_ids='[]',
        candidate_vars_ids='[101, 102]',
    )]).to_csv(target, index=False)

    saved = review.save_review_rules(
        results, {'air_temperature': [102]}, target)

    rule = saved.set_index('canonical_variable').loc['air_temperature']
    assert json.loads(rule.source_vars_ids) == [102]


def test_changing_recorded_manual_ids_updates_existing_selection(tmp_path):
    results = run_batch(tmp_path)
    target = tmp_path / 'rules.csv'
    pd.DataFrame([dict(
        network_id=2,
        canonical_variable='air_temperature',
        source_vars_ids='[101, 102]',
        source_vars_time_scales='{"101": "hourly", "102": "daily"}',
        recent_source_vars_ids='[101]',
        candidate_vars_ids='[101, 102]',
    )]).to_csv(target, index=False)

    saved = review.save_review_rules(results, {}, target)

    rule = saved.set_index('canonical_variable').loc['air_temperature']
    assert json.loads(rule.source_vars_ids) == [101]


def test_all_variables_notebook_scopes_manual_choices_by_network():
    notebook_path = Path(__file__).resolve().parents[1] / '2.all_variables_decide.ipynb'
    notebook = json.loads(notebook_path.read_text())
    source = ''.join(next(
        cell['source'] for cell in notebook['cells']
        if cell.get('id') == 'manual-choices'))

    network_1 = {'NETWORK_ID': 1}
    exec(compile(source, str(notebook_path), 'exec'), network_1)
    assert network_1['MANUAL_SOURCE_IDS_BY_NETWORK'] == {
        1: {'precipitation_amount': [429]},
        2: {
            'air_temperature': [434],
            'daily_max_temperature': [433],
            'daily_min_temperature': [435],
            'precipitation_amount': [442],
            'snow_depth': [450],
            'snowfall_amount': [451],
        },
        5: {
            'air_temperature': [1328, 1329],
            'snow_depth': [468, 1331],
        },
        6: {
            'daily_max_temperature': [470],
            'daily_min_temperature': [469],
            'precipitation_amount': [471],
        },
        9: {'air_temperature': [472, 693]},
        14: {
            'air_temperature': [701, 702],
            'precipitation_amount': [513],
        },
        17: {'precipitation_amount': [519]},
        70: {'air_temperature': [1305, 1306]},
        76: {'air_temperature': [1295, 1297]},
    }
    assert network_1['MANUAL_SOURCE_IDS'] == {
        'precipitation_amount': [429]}

    network_2 = {'NETWORK_ID': 2}
    exec(compile(source, str(notebook_path), 'exec'), network_2)
    assert network_2['MANUAL_SOURCE_IDS'] == {
        'air_temperature': [434],
        'daily_max_temperature': [433],
        'daily_min_temperature': [435],
        'precipitation_amount': [442],
        'snow_depth': [450],
        'snowfall_amount': [451],
    }

    network_76 = {'NETWORK_ID': 76}
    exec(compile(source, str(notebook_path), 'exec'), network_76)
    assert network_76['MANUAL_SOURCE_IDS'] == {
        'air_temperature': [1295, 1297]}


def test_missing_candidate_is_reported_without_stopping_other_variables(tmp_path):
    mappings = registry()
    mappings = mappings.loc[mappings.canonical_variable != 'snow_depth']
    with patch.object(review, 'select_candidate_stations', return_value=pd.DataFrame({'station_id': [1]})), \
         patch.object(review, 'fetch_candidate_observations', side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent):
        results = review.run_variable_reviews(None, mappings, tmp_path, plot_station_limit=1)
    assert len(results['rules']) == 5
    assert results['status'][-1]['status'] == 'no_candidates'
