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
import func_variable_review as review


def registry():
    return pd.DataFrame([
        dict(network_id=2, canonical_variable=name, vars_id=vid,
             net_var_name=f'candidate_{vid}', daily_aggregation='mean',
             priority=1, mapping_status='candidate')
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


def run_batch(tmp_path, eligible=None, observations=fake_observations, network_id=2):
    if eligible is None:
        eligible = pd.DataFrame({'station_id': range(1, 26)})
    with patch.object(review, 'select_candidate_stations', return_value=eligible) as select, \
         patch.object(review, 'fetch_candidate_observations', side_effect=observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent) as read:
        results = review.run_variable_reviews(
            None, registry(), tmp_path, network_id=network_id, plot_station_limit=1,
            source_station_limit=20, random_seed=42,
        )
        assert select.call_count == 6
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
    assert (second / 'review_results.json').is_file()
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
    for filename in ['time_series.pdf', 'cdf.pdf']:
        data = (folder / filename).read_bytes()
        assert len(re.findall(rb'/Type /Page\b', data)) == 6
    readout = pd.read_csv(folder / 'candidate_review.csv')
    assert len(readout) == 12
    assert 'total_station_count' not in readout
    assert 'mapping_status' not in readout
    assert readout.columns[-1] == 'priority'
    assert readout.columns[readout.columns.get_loc('daily_aggregation') + 1] == 'decision' 
    assert set(readout.loc[readout.vars_id == 101, 'recent_non_null_station_count']) == {20}
    assert (folder / 'qc_summary.csv').is_file()
    assert len(pd.read_csv(folder / 'station_conditions.csv')) == 240
    restored = json.loads((folder / 'review_results.json').read_text())
    assert restored['rules'] == results['rules']
    assert all(len(json.loads(row['source_station_ids'])) == 20 for row in results['rules'])
    with patch.object(review.pd, 'read_sql', side_effect=AssertionError('Save queried DB')):
        final = review.save_review_rules(restored, {'daily_min_temperature': [102]}, tmp_path / 'rules.csv')
    assert len(final) == 6
    chosen = final.set_index('canonical_variable').loc['daily_min_temperature']
    assert json.loads(chosen.source_vars_ids) == [101, 102]
    assert not {'rule_saved_at_utc', 'source_station_conditions', 'source_station_coverage'} & set(final)
    expected = ['source_vars_ids', 'recent_source_vars_ids',
                'recent_source_latest_observations']
    start = final.columns.get_loc('source_vars_ids')
    assert final.columns[start:start + 3].tolist() == expected
    run_final = pd.read_csv(folder / 'final_rules.csv')
    start = run_final.columns.get_loc('source_vars_ids')
    assert run_final.columns[start:start + 3].tolist() == expected


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
    before = target.read_bytes()
    saved = review.save_review_rules(results, {}, target)
    assert target.read_bytes() == before
    assert saved.source_vars_ids.tolist() == ['[102]']
    saved = review.save_review_rules(results, {'daily_min_temperature': [102]}, target)
    assert len(saved) == 2
    assert json.loads(saved.set_index('canonical_variable').loc[
        'daily_min_temperature', 'source_vars_ids']) == [102]


def test_missing_candidate_is_reported_without_stopping_other_variables(tmp_path):
    mappings = registry()
    mappings = mappings.loc[mappings.canonical_variable != 'snow_depth']
    with patch.object(review, 'select_candidate_stations', return_value=pd.DataFrame({'station_id': [1]})), \
         patch.object(review, 'fetch_candidate_observations', side_effect=fake_observations), \
         patch.object(review.pd, 'read_sql', side_effect=fake_recent):
        results = review.run_variable_reviews(None, mappings, tmp_path, plot_station_limit=1)
    assert len(results['rules']) == 5
    assert results['status'][-1]['status'] == 'no_candidates'
