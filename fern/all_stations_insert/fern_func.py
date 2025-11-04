import re
import logging
import os
from rapidfuzz import fuzz
import pandas as pd
import numpy as np

from crmprtd import Row
import logging

def normalize_name(name):
    """Normalize station/file names to make matching more robust."""
    name = name.lower().strip()
    # remove non-alphanumeric characters (e.g. '.', '-', '_', ' ')
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def names_match(a, b, threshold=40):
    """Return True if two names are similar above a threshold."""
    score = fuzz.ratio(normalize_name(a), normalize_name(b))
    return score >= threshold


def create_rows_from_dataframe(df_station, df_data, station_i, network_name='FLNRO-FERN'):
    """
    Convert a dataframe of station data into a list of Row objects for multiple variables.
    
    Parameters
    ----------
    df_station : pd.DataFrame
        Metadata dataframe with columns: lat, lon, native_id, station_name
    df_data : pd.DataFrame
        Station measurement data with a time column and variable columns
    station_i : int
        Index of the station in df_station
    network_name : str
        Name of the network (default 'FERN')
    
    Returns
    -------
    rows : list of Row
        List of Row objects for all variables
    native_id : str
        Station id
    """
    # --- Extract station info ---
    lat, lon, native_id, station_name = df_station.iloc[station_i][['lat', 'lon', 'native_id', 'station_name']]
    lat = lat.item()
    lon = lon.item()
    
    # --- Identify time and variable columns ---
    time_col = 'Date' if 'Date' in df_data.columns else df_data.columns[0]
    df_data[time_col] = pd.to_datetime(df_data[time_col], errors='coerce')
    variable_columns = [c for c in df_data.columns[1:] if ',' in c]

    # print(len(variable_columns))

    # --- Ensure numeric values ---
    for col in variable_columns:
        df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

    # --- Generate rows ---
    rows = []
    for col in variable_columns:
        parts = [p.strip() for p in col.split(',', 1)]
        variable_name = parts[0]
        unit = parts[1] if len(parts) > 1 else None

        for idx, r in df_data.iterrows():

            time_val = r[time_col]
            time_val = pd.Timestamp(time_val).to_pydatetime() if pd.notna(time_val) else None

            rows.append(
                Row(
                    time=time_val,
                    val=float(r[col]) if pd.notna(r[col]) else np.nan,
                    variable_name=variable_name,
                    unit=unit,
                    network_name=network_name,
                    station_id=native_id,
                    lat=lat,
                    lon=lon
                )
            )
    return rows, native_id




