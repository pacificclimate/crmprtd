# Network-2 mapping stage 1 findings

This prototype evaluates the three smallest network-2 station IDs:

| Station ID | Station | History ID | Frequency |
|---:|---|---:|---|
| 2654 | Brandywine | 3397 | 1-hourly |
| 2655 | Tantalus | 3398 | 1-hourly |
| 2657 | Mt. Strachan Precip | 3400 | 1-hourly |

The output is mapping evidence, not an approved production mapping.

## Candidate families

All three stations have modern candidates for the six canonical variables. They
also have legacy candidates for most variables. The modern/legacy pairs with
exact-timestamp overlap show very strong agreement:

| Variable | Stations | Overlap | Result |
|---|---|---:|---|
| Air temperature | All three | 22,646–27,131 | Correlation > 0.99999; median absolute difference about 0.024–0.025 °C |
| Hourly precipitation | All three | 22,252–27,378 | Correlation approximately 1; median absolute difference 0 mm |
| Snow depth | 2654, 2655 | 15,047–16,361 | Correlation > 0.9998; median absolute difference 0.189–0.230 cm |

This strongly suggests that modern air temperature and hourly precipitation are
normalized continuations or copies of the legacy sources. Snow depth is also
very close where overlap exists. A deterministic cutover rule is still required
so overlapping sources are not duplicated.

There is no exact-timestamp overlap for the dedicated Tmin, Tmax, or snowfall
pairs. Those mappings require daily/reset-behavior analysis.

## Important data-quality evidence

- Station 2654 contains extreme temperatures including -3497 °C and snow-depth
  sentinel -7999.
- Station 2657 modern snow depth and snowfall contain -6999 for every one of
  their 11,602 observations. These sources are `NO_VALID_DATA`, despite being
  structurally present.
- About 19–30% of modern hourly precipitation observations are negative under
  the current broad physical rule. Their coding convention must be examined;
  small negative values may be trace/correction codes.
- Legacy `HOURLY_PRECIPITATION` includes values such as 6999 and large negative
  sentinels.
- Slight negative snow-depth readings are common and may represent sensor
  offsets rather than missing data.

## Metadata issues

- `meta_station.min_obs_time` and `max_obs_time` end around 2011, while source
  observations continue through 2026. Coverage must be calculated from
  `obs_raw` by source.
- `meta_history.tz_offset` is empty. The observation-day timezone/reset rule is
  needed before authoritative daily aggregation.
- `HOURLY_PRECIPITATION` has a name suggesting hourly amounts but a cell method
  containing “sum within days interval: daily.” It must not be summed until its
  within-day behavior is confirmed.
- `*_snc_last_reset` values are running extrema. Their reset hour must be
  determined before choosing a daily value.

## Proposed next analysis

1. Identify explicit sentinel/code conventions for network 2.
2. Plot hourly running Tmin/Tmax by day to infer reset timing.
3. Compare reported extrema with extrema derived from cleaned point temperature.
4. Inspect precipitation codes and within-day repetition.
5. Define source cutover periods and approve the registry mappings.
6. Then implement pre-aggregation cleaning and flexible daily QC.

Detailed evidence is in `outputs/mapping_stage_1`, including coverage,
diagnostic, overlap, proposal tables, and seven PNG figures.
