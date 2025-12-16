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