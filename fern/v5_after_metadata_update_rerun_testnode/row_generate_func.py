from crmprtd import Row
import os
import pandas as pd

def extract_new_data_rows(row, data_path, network_name="BC-FERN"):
    """
    Extract time-value pairs outside the database range for a given station variable.
    If DB times are missing, all data are returned.

    Parameters
    ----------
    row : pd.Series
        A row from the data insert batch containing station/variable info.
    data_path : str
        Directory path containing the raw station CSV files.
    network_name : str, optional
        Network name for Row construction (default: 'BC-FERN').

    Returns
    -------
    list[Row]
        A list of Row objects for data outside the database time range.
    """
    # --- Extract info from the row ---
    variable_name_db = row['db_var_match']
    unit_db = row['unit_db']
    native_id = row['native_id_db']
    lat = float(row['lat_db'])
    lon = float(row['lon_db'])

    # --- Read the CSV file ---
    csv_file_name = row['station_file_name'] + '.csv'
    csv_path = os.path.join(data_path, csv_file_name)
    df_data = pd.read_csv(csv_path, encoding='latin1', low_memory=False)

    # --- Determine the time column ---
    time_col = 'Date' if 'Date' in df_data.columns else df_data.columns[0]
    df_data[time_col] = pd.to_datetime(df_data[time_col], errors='coerce')

    # --- Construct variable column name (e.g. "Rain, mm") ---
    variable_name = row['variable'] + ', ' + row['unit_raw']

    # --- Define DB time range ---
    earliest_db = pd.to_datetime(row.get('earliest_time_db', pd.NaT))
    latest_db = pd.to_datetime(row.get('latest_time_db', pd.NaT))

    # --- Select rows outside DB time range or all if DB times missing ---
    if pd.isna(earliest_db) or pd.isna(latest_db):
        df_outside = df_data[[time_col, variable_name]].dropna(subset=[variable_name])
    else:
        df_outside = df_data[
            (df_data[time_col] < earliest_db) | (df_data[time_col] > latest_db)
        ][[time_col, variable_name]].dropna(subset=[variable_name])

    df_outside = df_outside.reset_index(drop=True)

    # --- Build list of Row objects ---
    rows = [
        Row(
            time=row_i[time_col],
            val=row_i[variable_name],
            variable_name=variable_name_db,
            unit=unit_db,
            network_name=network_name,
            station_id=native_id,
            lat=lat,
            lon=lon
        )
        for _, row_i in df_outside.iterrows()
    ]

    return rows