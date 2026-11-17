import json
from pathlib import Path

import numpy as np
import pandas as pd


NOTEBOOK = Path(__file__).resolve().parents[1] / '0.candidate_discovery.ipynb'


def test_manual_candidate_id_replaces_auto_mapping_and_fills_metadata():
    notebook = json.loads(NOTEBOOK.read_text())
    source = ''.join(next(
        cell['source'] for cell in notebook['cells'] if cell.get('id') == 'review'))
    source = (
        "EXCLUDE = {(675, 'air_temperature')}\n"
        "MANUAL_CANDIDATES = {468: 'snow_depth'}\n\n"
        + source[source.index('reviewed = discovered_candidates.copy()'):]
    )
    discovered = pd.DataFrame([
        dict(vars_id=468, net_var_name='SNOW_ON_THE_GROUND',
             canonical_variable='snowfall_amount', unit='cm',
             daily_aggregation='sum', source_family='network5_auto',
             discovery_score=4.0, discovery_evidence='name',
             mapping_status='needs_review', priority=1),
        dict(vars_id=1331, net_var_name='snw_dpth', canonical_variable='snow_depth',
             unit='cm', daily_aggregation='fixed_hour', source_family='network5_auto',
             discovery_score=3.0, discovery_evidence='name',
             mapping_status='needs_review', priority=1),
        dict(vars_id=675, net_var_name='L_down_corr_Avg',
             canonical_variable='air_temperature', unit='W m-2',
             daily_aggregation='mean', source_family='network5_auto',
             discovery_score=2.0, discovery_evidence='description',
             mapping_status='needs_review', priority=1),
    ])
    catalog = pd.DataFrame([
        dict(vars_id=468, net_var_name='SNOW_ON_THE_GROUND', unit='cm'),
    ])
    namespace = {
        'pd': pd,
        'np': np,
        'display': lambda value: None,
        'NETWORK_ID': 5,
        'CANONICAL_VARIABLES': ('air_temperature', 'snow_depth', 'snowfall_amount'),
        'DISCOVERY_RULES': {
            'air_temperature': {'daily_aggregation': 'mean'},
            'snow_depth': {'daily_aggregation': 'fixed_hour'},
            'snowfall_amount': {'daily_aggregation': 'sum'},
        },
        'network_catalog': catalog,
        'discovered_candidates': discovered,
    }

    exec(compile(source, str(NOTEBOOK), 'exec'), namespace)

    reviewed = namespace['reviewed']
    manual = reviewed.loc[reviewed.vars_id == 468]
    assert len(manual) == 1
    row = manual.iloc[0]
    assert row.canonical_variable == 'snow_depth'
    assert row.net_var_name == 'SNOW_ON_THE_GROUND'
    assert row.unit == 'cm'
    assert row.daily_aggregation == 'fixed_hour'
    assert row.source_family == 'network5_reviewed'
    assert row.mapping_status == 'candidate'
    assert row.priority == 1
    excluded = reviewed.loc[reviewed.vars_id == 675]
    assert len(excluded) == 1
    assert excluded.iloc[0].mapping_status == 'excluded'


def test_network_6_persists_both_precipitation_exclusions():
    notebook = json.loads(NOTEBOOK.read_text())
    source = ''.join(next(
        cell['source'] for cell in notebook['cells'] if cell.get('id') == 'review'))
    override_source = source[:source.index('reviewed = discovered_candidates.copy()')]
    namespace = {'NETWORK_ID': 6}

    exec(override_source, namespace)

    assert namespace['EXCLUDE'] == {
        (1204, 'precipitation_amount'),
        (1207, 'precipitation_amount'),
        (1211, 'precipitation_amount'),
    }


def test_zero_observation_variables_need_no_frequency_overrides():
    notebook = json.loads(NOTEBOOK.read_text())
    source = ''.join(next(
        cell['source'] for cell in notebook['cells'] if cell.get('id') == 'review'))
    override_source = source[:source.index('reviewed = discovered_candidates.copy()')]

    network_5 = {'NETWORK_ID': 5}
    exec(override_source, network_5)
    assert network_5['SOURCE_TIME_SCALE_OVERRIDES'] == {}

    network_14 = {'NETWORK_ID': 14}
    exec(override_source, network_14)
    assert network_14['SOURCE_TIME_SCALE_OVERRIDES'] == {}


def test_empty_discovery_still_has_reviewable_mapping_columns():
    notebook = json.loads(NOTEBOOK.read_text())
    sources = {
        cell.get('id'): ''.join(cell['source'])
        for cell in notebook['cells'] if cell.get('id') in {'discover', 'review'}
    }
    namespace = {
        'pd': pd,
        'np': np,
        're': __import__('re'),
        'display': lambda value: None,
        'network_catalog': pd.DataFrame(),
        'CANONICAL_VARIABLES': (),
        'CANONICAL_RULES': {},
        'DISCOVERY_RULES': {},
        'NETWORK_ID': 999,
        'MIN_SCORE': 3,
    }

    exec(compile(sources['discover'], str(NOTEBOOK), 'exec'), namespace)
    exec(compile(sources['review'], str(NOTEBOOK), 'exec'), namespace)

    assert namespace['reviewed'].empty
    assert {'vars_id', 'canonical_variable', 'mapping_status', 'priority'} <= set(
        namespace['reviewed'].columns)


def test_precipitation_discovery_keeps_rolling_past_24_hour_for_review():
    notebook = json.loads(NOTEBOOK.read_text())
    sources = {
        cell.get('id'): ''.join(cell['source'])
        for cell in notebook['cells'] if cell.get('id') in {'rules', 'discover'}
    }
    catalog = pd.DataFrame([
        dict(vars_id=710, net_var_name='pcpn_amt_pst24hrs', unit='mm',
             standard_name='lwe_thickness_of_precipitation_amount',
             cell_method='time: sum over hours', display_name='Precipitation',
             short_name='pcpn', long_description='Past 24 hours'),
        dict(vars_id=706, net_var_name='pcpn_amt_pst1hr', unit='mm',
             standard_name='lwe_thickness_of_precipitation_amount',
             cell_method='time: sum over hours', display_name='Precipitation',
             short_name='pcpn', long_description='Past 1 hour'),
    ])
    namespace = {
        'pd': pd, 're': __import__('re'), 'display': lambda value: None,
        'network_catalog': catalog, 'NETWORK_ID': 14, 'MIN_SCORE': 3,
        'CANONICAL_VARIABLES': ('precipitation_amount',),
        'CANONICAL_RULES': {
            'precipitation_amount': type('Rule', (), {'unit': 'mm'})()},
    }

    exec(compile(sources['rules'], str(NOTEBOOK), 'exec'), namespace)
    exec(compile(sources['discover'], str(NOTEBOOK), 'exec'), namespace)

    discovered_ids = set(namespace['discovered_candidates'].vars_id.astype(int))
    assert 706 in discovered_ids
    assert 710 in discovered_ids


def test_discovery_saves_station_count_and_time_scale_for_all_candidates():
    notebook = json.loads(NOTEBOOK.read_text())
    source = ''.join(next(
        cell['source'] for cell in notebook['cells'] if cell.get('id') == 'final'))
    reviewed = pd.DataFrame([
        dict(vars_id=501, net_var_name='Rainmm',
             canonical_variable='precipitation_amount', daily_aggregation='sum',
             priority=1, source_family='network11_auto',
             mapping_status='needs_review'),
        dict(vars_id=1268, net_var_name='TempC_30_cm',
             canonical_variable='air_temperature', daily_aggregation='mean',
             priority=1, source_family='network11_auto',
             mapping_status='excluded'),
    ])
    captured = {}

    def add_counts(engine, mappings, network_id):
        assert network_id == 11
        return mappings.assign(network_station_count=mappings.vars_id.map(
            {501: 43, 1268: 0}))

    def save(network_id, mappings, path):
        captured['mappings'] = mappings.copy()
        return mappings.assign(network_id=network_id)

    def add_time_scales(engine, mappings, metadata, network_id, overrides):
        assert network_id == 11
        assert overrides == {}
        output = mappings.copy()
        output.loc[output.network_station_count.eq(0), 'mapping_status'] = 'excluded'
        return output.assign(source_time_scale=output.vars_id.map(
            {501: 'hourly'}))

    def add_daily_processing(mappings, metadata, overrides=None):
        captured['daily_processing_called'] = True
        assert overrides is None
        output = mappings.copy()
        output.loc[output.source_time_scale.eq('daily'), 'daily_aggregation'] = 'as_is'
        return output

    namespace = {
        'reviewed': reviewed,
        'engine': object(),
        'NETWORK_ID': 11,
        'NETWORK_DIR': Path('/tmp/network_11'),
        'OUTPUT_PREFIX': 'net11_',
        'add_network_station_counts': add_counts,
        'add_candidate_time_scales': add_time_scales,
        'add_candidate_daily_processing': add_daily_processing,
        'save_candidate_mappings': save,
        'network_catalog': pd.DataFrame(),
        'SOURCE_TIME_SCALE_OVERRIDES': {},
        'display': lambda value: None,
    }

    exec(compile(source, str(NOTEBOOK), 'exec'), namespace)

    saved = captured['mappings'].set_index('vars_id')
    assert captured['daily_processing_called']
    assert saved.network_station_count.to_dict() == {501: 43, 1268: 0}
    assert saved.loc[501, 'source_time_scale'] == 'hourly'
    assert pd.isna(saved.loc[1268, 'source_time_scale'])
    assert saved.mapping_status.to_dict() == {
        501: 'needs_review', 1268: 'excluded'}
    assert 'daily_boundary_hour' not in saved
    assert 'daily_time_basis' not in saved
    assert 'daily_processing_status' not in saved
