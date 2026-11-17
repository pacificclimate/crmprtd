import json
from pathlib import Path

import pandas as pd
import pytest
import sqlalchemy as sa


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / '3.combine_candidate_mappings.ipynb'
OUTPUT_COLUMNS = [
    'network_id', 'canonical_variable', 'vars_id', 'net_var_name',
    'standard_name', 'cell_method', 'long_description', 'display_name',
    'network_station_count', 'source_time_scale', 'daily_aggregation',
]


def load_combiner():
    """Load the production function from notebook cells tagged for testing."""
    notebook = json.loads(NOTEBOOK.read_text())
    namespace = {'PROJECT_ROOT': ROOT}
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        if 'testable' not in cell.get('metadata', {}).get('tags', []):
            continue
        exec(''.join(cell['source']), namespace)
    return namespace['combine_candidate_mappings']


def write_mapping(networks_dir, network_id, rows, *, optional_columns=True):
    folder = networks_dir / f'network_{network_id}'
    folder.mkdir(parents=True)
    frame = pd.DataFrame(rows)
    frame['network_id'] = network_id
    if optional_columns:
        frame['network_station_count'] = frame.get('network_station_count', 3)
        frame['source_time_scale'] = frame.get('source_time_scale', 'hourly')
    frame['priority'] = range(1, len(frame) + 1)
    frame['source_family'] = f'network{network_id}_auto'
    frame['mapping_status'] = 'needs_review'
    path = folder / f'net{network_id}_candidate_mappings.csv'
    frame.to_csv(path, index=False)
    return path


def write_metadata_database(tmp_path, rows):
    database = tmp_path / 'metadata.sqlite'
    engine = sa.create_engine(f'sqlite:///{database}')
    pd.DataFrame(rows).to_sql('meta_vars', engine, index=False)
    engine.dispose()
    return f'sqlite:///{database}'


def combine_with_database(networks_dir, output, db_url):
    engine = sa.create_engine(db_url)
    try:
        return load_combiner()(networks_dir, output, engine)
    finally:
        engine.dispose()


def test_combines_normalized_files_with_metadata_and_stable_order(tmp_path):
    networks = tmp_path / 'networks'
    source_10 = write_mapping(networks, 10, [dict(
        vars_id=900, net_var_name='rain', canonical_variable='precipitation_amount',
        daily_aggregation='sum')], optional_columns=False)
    source_2 = write_mapping(networks, 2, [
        dict(vars_id=102, net_var_name='temp_b', canonical_variable='air_temperature',
             daily_aggregation='mean', network_station_count=4,
             source_time_scale='hourly'),
        dict(vars_id=101, net_var_name='temp_a', canonical_variable='air_temperature',
             daily_aggregation='mean', network_station_count=5,
             source_time_scale='daily'),
    ])
    original_10 = source_10.read_bytes()
    original_2 = source_2.read_bytes()
    output = networks / 'all_networks_candidate_mappings.csv'
    db_url = write_metadata_database(tmp_path, [
        dict(vars_id=101, network_id=2, standard_name='air_temperature',
             cell_method='time: mean', long_description='Temperature A',
             display_name='Temperature'),
        dict(vars_id=102, network_id=2, standard_name='air_temperature',
             cell_method='time: mean', long_description='Temperature B',
             display_name='Temperature'),
        dict(vars_id=900, network_id=10, standard_name='precipitation_amount',
             cell_method='time: sum', long_description='Rain total',
             display_name='Precipitation'),
    ])

    combined = combine_with_database(networks, output, db_url)

    assert combined.columns.tolist() == OUTPUT_COLUMNS
    assert list(zip(combined.network_id, combined.vars_id)) == [
        (2, 101), (2, 102), (10, 900)]
    assert pd.isna(combined.loc[combined.vars_id.eq(900), 'network_station_count']).all()
    assert pd.isna(combined.loc[combined.vars_id.eq(900), 'source_time_scale']).all()
    assert combined.loc[combined.vars_id.eq(101), 'long_description'].item() == (
        'Temperature A')
    pd.testing.assert_frame_equal(pd.read_csv(output), combined, check_dtype=False)
    assert source_10.read_bytes() == original_10
    assert source_2.read_bytes() == original_2


def test_rejects_folder_filename_and_row_network_id_mismatch(tmp_path):
    networks = tmp_path / 'networks'
    source = write_mapping(networks, 2, [dict(
        vars_id=101, net_var_name='temp', canonical_variable='air_temperature',
        daily_aggregation='mean')])
    frame = pd.read_csv(source)
    frame['network_id'] = 99
    frame.to_csv(source, index=False)
    db_url = write_metadata_database(tmp_path, [dict(
        vars_id=101, network_id=2, standard_name='air_temperature',
        cell_method='time: mean', long_description='Temperature',
        display_name='Temperature')])

    with pytest.raises(ValueError, match='network_id.*network_2'):
        combine_with_database(
            networks, networks / 'all_networks_candidate_mappings.csv', db_url)


def test_rejects_empty_network_directory(tmp_path):
    networks = tmp_path / 'networks'
    networks.mkdir()
    db_url = write_metadata_database(tmp_path, [dict(
        vars_id=1, network_id=1, standard_name='air_temperature',
        cell_method='time: mean', long_description='Temperature',
        display_name='Temperature')])

    with pytest.raises(ValueError, match='No candidate mapping files found'):
        combine_with_database(
            networks, networks / 'all_networks_candidate_mappings.csv', db_url)


def test_rejects_candidate_without_meta_vars_row(tmp_path):
    networks = tmp_path / 'networks'
    write_mapping(networks, 2, [dict(
        vars_id=101, net_var_name='temp', canonical_variable='air_temperature',
        daily_aggregation='mean')])
    db_url = write_metadata_database(tmp_path, [dict(
        vars_id=999, network_id=2, standard_name='air_temperature',
        cell_method='time: mean', long_description='Other variable',
        display_name='Temperature')])

    with pytest.raises(
        ValueError, match=r'Missing meta_vars rows for vars_ids: \[101\]'):
        combine_with_database(
            networks, networks / 'all_networks_candidate_mappings.csv', db_url)
