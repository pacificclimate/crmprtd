# Inserts are append-only

The Insert stage writes Observations with `ON CONFLICT DO NOTHING`: duplicate
Observations are ignored, never updated. We chose this over an upsert
(`ON CONFLICT DO UPDATE`) for two reasons:

1. **Speed.** Bulk inserts that ignore conflicts avoid the per-row cost and
   contention of updating existing rows, which matters at the volumes crmprtd
   ingests.
2. **Immutability.** A stored Observation records what a Station reported at a
   given time; it should never change.

## Consequences

- Infill (backfill) can fill gaps but **cannot correct** an already-stored value
  by re-inserting it — re-running over existing data is harmless but a no-op for
  those rows.
- Correcting bad data is therefore not done by overwriting. Instead, an
  Observation later judged incorrect is **flagged as unsuitable for scientific
  use** downstream, leaving the original value intact.
