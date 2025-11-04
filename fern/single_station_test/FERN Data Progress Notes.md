# FERN Data Progress Notes

Hi James, John,

Good news! John and I think we managed to get some FERN data into the obs-raw database. I wanted to share what happened, some things we're wondering about, and get your thoughts.

## What Happened

- Tried to insert 120 items (12 variables × 10 time points) from the Barren station.
- Source file: `/storage/data/projects/crmp/data/fern/FERNNorth2024_VF/WxData24/Barren.csv`
- Log says: `"Bulk insert progress: 21 inserted, 99 skipped, 0 failed"`
- We checked the database: the 21 inserted records are all NaN values, and the 99 skipped ones were already in the database.

### Questions

- Should NaN values be inserted at all?
- Is it normal for existing items to be skipped automatically?

If both answers are "yes," then I think this was a successful test!

---

## What I Did

I had to manually fix three main data matching issues in the Fern data under `/WxData24` so it would fit the obs_row format and could be inserted.

The scripts I used:
1. Station name matching (`1.generate_rows_all_stations_seperate_pkl.py`)
2. Variable name matching (`2.variable_match_submit.ipynb`)
3. Unit matching (`3.unit_match.ipynb`)
4. Insert (`4.insert.py`)

All code is pushed to [GitHub](https://github.com/pacificclimate/crmprtd/tree/FERN_TL/fern).

---

### Issues I Ran Into

#### 1. Station Name Matching

The station names in `20241125 MeteorologicalNetworks-FERN-VF-shared.xlsx` and `/WxData24` aren't exactly the same. I used `rapidfuzz` to help sort them out, plus some manual checks. The matches look reasonable.

Example log:
``` md
2025-10-16 20:53:03 - INFO - Processing station: Atlin School with file: Atlin school
2025-10-16 20:53:03 - INFO - Processing station: BarrenWx with file: Barren
2025-10-16 20:53:03 - INFO - Processing station: BlackhawkWx with file: Blackhawk
2025-10-16 20:53:03 - INFO - Processing station: BoulderWx with file: BoulderCr
2025-10-16 20:53:03 - INFO - Processing station: BowronPit with file: Bowron Pit
2025-10-16 20:53:03 - INFO - Processing station: BulkleyWx with file: Bulkley PGTIS 1
2025-10-16 20:53:03 - INFO - Processing station: CPFWx with file: CPF PGTIS 3
2025-10-16 20:53:03 - INFO - Processing station: Canoe Mountain Stn with file: Canoe
2025-10-16 20:53:03 - INFO - Processing station: Caribou Pass with file: Caribou Pass
2025-10-16 20:53:03 - INFO - Processing station: ChapmanWx with file: Chapman
2025-10-16 20:53:03 - INFO - Processing station: ChiefLakeWx with file: ChiefLk
2025-10-16 20:53:03 - INFO - Processing station: CoalmineWx with file: Coalmine
2025-10-16 20:53:04 - INFO - Processing station: CrookedLk with file: Crooked Lake
2025-10-16 20:53:04 - INFO - Processing station: CrystalWx with file: CrystalLk
2025-10-16 20:53:04 - INFO - Processing station: Dennis with file: Dennis
2025-10-16 20:53:04 - INFO - Processing station: DunsterWx with file: Dunster
2025-10-16 20:53:04 - INFO - Processing station: EndakoWx with file: Endako
2025-10
...
```

#### 2. Variable Name Matching

This is the trickiest part and probably needs input from the FERN data group.

- Variable names in FERN data (like `WxData24/Barren.csv`) don't always match what's in `meta_vars`.
- Used `rapidfuzz` for fuzzy matching. Here are some results:

```md
Matching results:
Rain                 -> Rainmm               (score=80.0)
Pressure             -> Pressurembar         (score=80.0)
Temp                 -> TempC                (score=88.9)
RH                   -> RH                   (score=100.0)
DewPt                -> DewPtC               (score=90.9)
Wind Speed           -> WindSpeedms          (score=85.7)
Gust Speed           -> GustSpeedms          (score=85.7)
Wind Direction       -> WindDirection        (score=96.3)
Solar Radiation      -> SolarRadiationWm     (score=90.3)
Wetness              -> Wetness              (score=100.0)
Snow depth raw       -> Snow_Depth           (score=66.7)
Snow depth           -> Snow_Depth           (score=80.0)
Water Content        -> Water_Content_m3_m3_5_cm (score=64.9)
WC_cal               -> Wind_n               (score=33.3)
Soil Temp            -> Soil_Temp            (score=88.9)
Temp 2               -> TempC                (score=72.7)
RH 2                 -> RH                   (score=66.7)
DewPt 2              -> DewPtC               (score=76.9)
```
And there are 6 wrong cases for me,

```md
Snow depth raw       -> Snow_Depth           (score=66.7)  what the raw means?

Water Content        -> Water_Content_m3_m3_5_cm (score=64.9) which depth?

WC_cal               -> Wind_n               (score=33.3). Calibrated soil water content?, cubic meter of water per cubic meter of soil

Temp 2               -> TempC                (score=72.7) no match in db

RH 2                 -> RH                   (score=66.7) no match in db

DewPt 2              -> DewPtC               (score=76.9) no match in db
```

The left variables need to be double check as well.

To continue the next steps, I removed the Rows objects of these 6 questionable variables, thus we have 12 variables × 10 time points left.


#### 3. Units Matching

Some units in FERN data are marked differently than in `meta_vars`. I fixed the labels, but didn't change any values.

The variables with unit mismatches are:
```md
Variables with unit differences:
[('Pressurembar', ('mbar', 'millibar')),
 ('TempC', ('°C', 'celsius')),
 ('DewPtC', ('°C', 'celsius')),
 ('WindSpeedms', ('m/s', 'm s-1')),
 ('GustSpeedms', ('m/s', 'm s-1')),
 ('WindDirection', ('ø', 'degree')),
 ('SolarRadiationWm', ('W/m²', 'W m-2')),
 ('Soil_Temp', ('°C', 'celsius'))]
```

#### 4. Insert

After matching names and units, the rows can be inserted. 

The code in `4.insert.py` is copied from `process.py`. Logging is set up in `/workspaces/crmprtd/crmprtd/__init__.py`.

---

## Next steps

Not sure if it's time to look at Ted's files and update the database, so let me know what you think!

- Should we double-check if all FERN data is in the database? Maybe try inserting everything under `/WxData24` and see what happens?
- Go through Ted's sheet and figure out what to do with it?
- Fill in any missing knowledge for future work.

---


### Stuff John Showed Me Recently

- Smart debugging tricks
- DataGrip for better DB interaction and SQL queries
- How to use logging
- Git basics (add, commit, push, pull)
- Docker/dev containers for development
- Setting up `.pgpass` for DB access

---

Let me know what you think or if you have any advice!