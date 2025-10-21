import pycds
from crmprtd import Row
import os
import pickle
import pandas as pd
import numpy as np
from natsort import natsorted
from natsort import natsort_keygen


print('Import Done!')

path = '/fern_data/FERNNorth2024_VF/'
df_data = pd.read_excel(os.path.join(path, '20241125 MeteorologicalNetworks-FERN-VF-shared.xlsx'))
# Sort by station_name in "natural" order
df_data = df_data.sort_values(by='station_name', key=natsort_keygen())


station_id = 0

lat, lon, native_id, station_name = df_data.iloc[station_id][['lat', 'lon', 'native_id', 'station_name']]


path = '/fern_data/FERNNorth2024_VF/WxData24'
csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
# Sort in natural order
csv_files = natsorted(csv_files)

file_path = os.path.join(path, csv_files[station_id])
station_name_from_file = os.path.splitext(csv_files[station_id])[0]  # take part before ".csv"

print(station_name + ' vs. ' + station_name_from_file)


df = pd.read_csv(file_path, encoding='latin1', low_memory=False, nrows=10)
time_col = 'Date' if 'Date' in df.columns else df.columns[0]
df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
variable_columns = [c for c in df.columns if ',' in c]

for col in variable_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # ensure numeric, NaNs are np.nan

rows = []
for col in variable_columns:
    parts = [p.strip() for p in col.split(',', 1)]
    variable_name = parts[0]
    unit = parts[1] if len(parts) > 1 else None

    for idx, r in df.iterrows():
        rows.append(
            Row(
                time=r[time_col].to_pydatetime() if pd.notna(r[time_col]) else None,
                val=float(r[col]) if pd.notna(r[col]) else np.nan,  # force float
                variable_name=variable_name,
                unit=unit,
                network_name='FERN',
                station_id=native_id,
                lat=lat,
                lon=lon
            )
        )

with open('rows_output_' + native_id + '.pickle', 'wb') as f:
    pickle.dump(rows, f)
