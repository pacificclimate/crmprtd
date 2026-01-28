### The update of searching **Vanessa ** Summary

- The update of searching **Vanessa Foord** has been done (32 stations, span from lines 1998-2041), including:
  - `station_name`, `lat`, `lon`, `elev` in `meta_history`
  - `native_id` in `meta_station`  
- All updates are applied according to **Ted's sheet**, with two Manual adjustments applied:
    1. `Station_name`: `SmithersCmpd` (correcting `SmitherCmpd` in both Ted's Line 2036 and Vanessa's sheet)
    2. `Station Dennis`: updated coordinates and elevation `[54.76159, -127.46765, 895]`
   
- **Comparison with Vanessa's sheet:**
  - `lat`, `lon`, `elev` generally match.
  - **Exception:**  
    - Station `Kluskus`  
      - `native_id` in Ted's sheet: `BednestiWx`  
      - `native_id` in Vanessa's sheet: `SBSmc3Wx`

- **Comparison with marked changes in Ted's sheet:**
  - `station_name` modifications are consistent.
  - `lat`, `lon`, `elev` values are not completely identical; current update follows Ted's sheet.
  
 

### The update of searching **'-> BC-FERN' **, `Additional/data in hand`  Summary

For the station `SeebachWx`, the lon should be `-122.058` in Ted's sheet, the left pcds part is correct

`Mayson Lake - M4` has no elev information

The left marked change and that in Ted's sheets are all correct



After I update all the lat, lon, I think the _the_geom need to be updated


### 10.Concatenate
- In the 10.Concatenate, new_native_id 469, 452, T035, 77, E271963, E238705, 543 donot exist

- For the terms masked as Concatenate, after concatenating, do we need to delete the old station in database?

- Name change of these stations? Change the name of new native_id?

- Horseshoe Bay -> T035, the attribution change


### 11. Additional: Replaces  SBC19 - Concatenate data record

Some of the old_native_id are not exist. 

[  1/22] old_native_id=SBC19           | → EXISTS
[  2/22] old_native_id=24547           | → EXISTS
[  3/22] old_native_id=25672           | → NOT EXISTS
[  4/22] old_native_id=bc65            | → EXISTS
[  5/22] old_native_id=bo107           | → NOT EXISTS
[  6/22] old_native_id=ch107           | → NOT EXISTS
[  7/22] old_native_id=co107           | → NOT EXISTS
[  8/22] old_native_id=de107           | → NOT EXISTS
[  9/22] old_native_id=di107           | → NOT EXISTS
[ 10/22] old_native_id=Do107           | → NOT EXISTS
[ 11/22] old_native_id=gr107           | → NOT EXISTS
[ 12/22] old_native_id=ha107           | → NOT EXISTS
[ 13/22] old_native_id=hat107          | → NOT EXISTS
[ 14/22] old_native_id=ma107           | → NOT EXISTS
[ 15/22] old_native_id=mab107          | → NOT EXISTS
[ 16/22] old_native_id=qu107           | → NOT EXISTS
[ 17/22] old_native_id=SBC15           | → NOT EXISTS
[ 18/22] old_native_id=SBC25           | → NOT EXISTS
[ 19/22] old_native_id=SBC35           | → EXISTS
[ 20/22] old_native_id=si107           | → NOT EXISTS
[ 21/22] old_native_id=so107           | → NOT EXISTS
[ 22/22] old_native_id=su107           | → NOT EXISTS


### 12. Replaced by AGBCSUMASP - move data record, delete station

For the old stations, if search by native_id, can't find these stations. Using station_id, can find these stations;

That means, the Native IDs shown in the spreadsheet are inconsistent with that in the database.

Searching by station_id, station 1538, 1523, 3102, 3110 are non-exist.

The old station `1508` exist, while the new one `AMGL019` does not exist.




### 15. The New station insertion, need to motify the network name first

### 16. The two "Missing data", anything I can do?
The two "Missing Data", also need to change attribution



### Side probelems

one native_id but points to two station_ids. If under different network, maybe fine? If under the same network, might because accidentally repeatedly creating the new stations. So should check out and constrain.