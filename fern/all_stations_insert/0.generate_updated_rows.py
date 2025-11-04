from crmprtd import Row
import logging
import os
import pickle
import pandas as pd
import numpy as np
from natsort import natsorted
from natsort import natsort_keygen
from pprint import pprint
from collections import Counter
from collections import defaultdict

import re
from rapidfuzz import fuzz
from crmprtd import infer
from fern_func import *
from sql_func import *
from rapidfuzz import process

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)

# --- Main workflow ---
# --- read data ---
meta_path = '/fern_data/FERNNorth2024_VF/20241125 MeteorologicalNetworks-FERN-VF-shared.xlsx'
data_path = '/fern_data/FERNNorth2024_VF/WxData24'

df_station = pd.read_excel(meta_path)
df_station = df_station.sort_values(by='station_name', key=natsort_keygen())

csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
# Sort in natural order
csv_files = natsorted(csv_files)

# --- output folder ---
output_folder = '/workspaces/crmprtd/fern/all_stations_insert/rows_output/'
os.makedirs(output_folder, exist_ok=True)

def fuzzy_match_var(file_var, db_vars, threshold=85):
    # Get best match and score
    match, score, _ = process.extractOne(file_var, db_vars, scorer=fuzz.ratio)
    # Get all matches for additional info
    matches = process.extract(file_var, db_vars, limit=1, scorer=fuzz.ratio)
    # Keep original name if score below threshold
    result = match if score >= threshold else file_var
    return result, score, matches

def obtain_rows(df_station, data_path, csv_file, station_i, nrows=100):
    """
    Read a station CSV, create and clean observation rows.

    Parameters
    ----------
    df_station : pd.DataFrame
        DataFrame containing station metadata (e.g., name, id).
    data_path : str
        Path to folder containing CSV files.
    csv_file : str
        The specific CSV file name.
    station_i : int
        Index of the station in df_station.
    nrows : int
        Optional: number of rows to read (for testing/preview).

    Returns
    -------
    rows_clean : list
        List of cleaned observation rows.
    native_id : any
        Native ID returned by create_rows_from_dataframe().
    summary : dict
        Small summary containing station_name, total_vars, and variable counts.
    """
    station_name = df_station.iloc[station_i]['station_name']
    station_file_name = os.path.splitext(csv_file)[0]

    # --- Read file ---
    csv_path = os.path.join(data_path, csv_file)
    df_data = pd.read_csv(csv_path, encoding='latin1', low_memory=False, nrows=nrows)

    # --- Generate raw rows from the Fern file ---
    rows, native_id = create_rows_from_dataframe(df_station, df_data, station_i)

    # --- Clean rows (remove NaN values) ---
    rows_clean = [r for r in rows if hasattr(r, "val") and not pd.isna(r.val)]

    # --- Count variables ---
    var_counts = Counter(r.variable_name for r in rows_clean if hasattr(r, "variable_name"))
    total_var_counts = sum(var_counts.values())

    summary = {
        "station_name": station_name,
        "file_name": station_file_name,
        "total_var_counts": total_var_counts,
        "unique_variables": len(var_counts),
        "variable_counts": var_counts
    }

    return rows_clean, native_id, summary

def updated_rows_only_changed(rows_clean, db_vars_unit, threshold=60):
    """
    Return only rows where variable name was updated (not unchanged).
    """
    updated_rows_clean = []
    updated_vars = []

    updated_var_names = set()
    unchanged_var_names = set()

    db_vars = list(db_vars_unit.keys())

    print(db_vars)

    for r in rows_clean:
        best_match, score, matches = fuzzy_match_var(r.variable_name, db_vars, threshold=threshold)
        if score >= threshold and best_match in db_vars_unit:
            new_var = best_match
            new_unit = db_vars_unit[best_match]
            updated_vars.append((r.variable_name, new_var, r.unit, new_unit))
            updated_rows_clean.append(
                Row(
                    time=r.time,
                    val=r.val,
                    variable_name=new_var,
                    unit=new_unit,
                    network_name=r.network_name,
                    station_id=r.station_id,
                    lat=r.lat,
                    lon=r.lon
                )
            )
            updated_var_names.add(r.variable_name)
        
        elif score < threshold:
            unchanged_var_names.add(r.variable_name)

    print(f"\nStation {station_name}:")
    print(f"  {len(updated_var_names)} unique variables updated:")
    for var in sorted(updated_var_names):
        print(f"    UPDATED: {var}")

    print(f"  {len(unchanged_var_names)} unique variables unchanged:")
    for var in sorted(unchanged_var_names):
        print(f"    UNCHANGED: {var}")

    return updated_rows_clean, updated_var_names, unchanged_var_names


# --- Containers for all stations ---
all_updated_rows = []
all_updated_vars = []
all_unchanged_vars = []
all_total_rows = []  # store total rows per station
updated_total_rows = []  # store total rows per station

csv_path = "/workspaces/crmprtd/fern/all_stations_insert/fern_station_db_variable_compare_summary.csv"
var_compare_summary = pd.read_csv(csv_path)

threshold = 80

for station_i, csv_file in enumerate(csv_files):
    rows_clean, native_id, summary_row = obtain_rows(df_station, data_path, csv_file, station_i, nrows=10)
    station_name = summary_row['station_name']
    total_rows_count = len(rows_clean)
    all_total_rows.append({'station_name': station_name, 'total_rows': total_rows_count})

    var_station_line = var_compare_summary[var_compare_summary['station_name'] == station_name]
    if var_station_line.empty:
        print(f"Skipping {station_name}: not found in summary.")
        continue

    # Combine vars_in_both and vars_only_db for db_vars
    db_vars = []
    for col in ['vars_in_both', 'vars_only_db']:
        val = var_station_line.iloc[0][col]
        if isinstance(val, str):
            db_vars += eval(val)
        else:
            db_vars += val

    db_vars_unit = eval(var_station_line.iloc[0]['var_and_unit_db']) if isinstance(var_station_line.iloc[0]['var_and_unit_db'], str) else var_station_line.iloc[0]['var_and_unit_db']

    # print(rows_clean)

    updated_rows, updated_vars, unchanged_vars = updated_rows_only_changed(rows_clean, db_vars_unit, threshold=threshold)

    # --- Append to global containers ---
    all_updated_rows.extend(updated_rows)
    all_updated_vars.append({'station_name': station_name, 'updated_vars': updated_vars})
    all_unchanged_vars.append({'station_name': station_name, 'unchanged_vars': unchanged_vars})
    updated_rows_count = len(updated_rows)
    updated_total_rows.append({'station_name': station_name, 'updated_rows': updated_rows_count})


# --- Save all_updated_rows to a single pickle file ---
pickle_file_path = output_folder + "updated_10_rows_all_stations.pkl"
with open(pickle_file_path, "wb") as f:
    pickle.dump(all_updated_rows, f)

# --- Combine summary with counts ---
combined = []
for upd, unchg, total_row, updated_row in zip(all_updated_vars, all_unchanged_vars, all_total_rows, updated_total_rows):
    updated_list = upd["updated_vars"] if upd["updated_vars"] else []
    unchanged_list = unchg["unchanged_vars"] if unchg["unchanged_vars"] else []
    total_rows = total_row["total_rows"]
    updated_row = updated_row["updated_rows"]

    combined.append({
        "station_name": upd["station_name"],
        "updated_row": total_rows,
        "updated_rows_count": updated_row,   # number of variables updated
        "updated_vars": ", ".join(updated_list),
        "num_updated_vars": len(updated_list),
        "unchanged_vars": ", ".join(unchanged_list),
        "num_unchanged_vars": len(unchanged_list)
    })

df_summary = pd.DataFrame(combined)

# --- Save to CSV ---
df_summary.to_csv(output_folder + "updated_vars_summary_all_stations.csv", index=False)

print("✅ Summary CSV saved with total rows and updated counts per station.")
