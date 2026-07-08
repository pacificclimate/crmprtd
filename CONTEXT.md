# crmprtd

crmprtd ("CRMP Real-Time Daemon") acquires near-real-time weather observations
from a variety of government agencies and inserts them into PCIC's PCDS-type
climate databases (e.g. CRMP, Metnorth). Despite the historical name,
acquisition is not real-time and nothing runs as a daemon — the programs run as
scheduled (hourly/daily) cron jobs.

## Language

### Pipeline and phases

**Pipeline**:
The conceptual end-to-end flow that acquires Observations from a Data source and
stores them in the database. Realized today as the `crmprtd_pipeline` command,
run from cron, which chains the phases together as OS subprocesses. Referring to
the project as a whole, say "crmprtd"; reserve "Pipeline" for the flow.

**Download**:
The first phase: obtain raw observation data from a Data source and emit it as
raw text/XML. Network-specific.

**Process**:
The second phase: everything after Download — turn raw data into Observations
and store them. Encompasses the Normalize, Align, and Insert stages. Realized as
the `crmprtd_process` command. (The original design deliberately split the
program into just these two phases, Download and Process; the code's package
docstring instead bills Normalize/Align/Insert as co-equal top-level phases —
this glossary treats them as stages within Process.)

**Normalize**:
A stage within Process: network-specific transformation of raw downloaded data
into Rows. Requires no database access — only network-specific knowledge.

**Align**:
A stage within Process: match or create the database History and Variable
records each Row needs, producing Obs. Common to all Networks.

**Insert**:
A stage within Process: bulk-write Obs to the database, reporting
successes/failures. Common to all Networks. Insert is **append-only**: duplicate
Observations are ignored (`ON CONFLICT DO NOTHING`), never updated — so an
already-stored Observation cannot be corrected by re-inserting it.

**Infill**:
Backfilling historical Observations for a past date range by re-running the
Download and Process phases over that range, split into time chunks sized to
respect each Data source's per-request limits and its window of available
history. Purely gap-filling: because Insert is append-only, re-running over
already-stored data is harmless but does not correct existing values.
_Synonym_: backfill (infill is preferred)

**Cache**:
The optional saving of raw downloaded data to disk (via `tee`) between the
Download and Process phases, so a Process run can be re-driven from saved raw
data without re-downloading.

**Infer**:
An optional, read-only phase (run via `crmprtd_process --infer`) that examines a
batch of Rows and reports which database metadata records (Variables, Stations,
Histories) would need to be created to support them, without inserting any
Observations. Advisory only — a human decides what to actually create, because
required Variable metadata (e.g. `cell_method`, descriptions) cannot be derived
from the feed and not every reported quantity is worth tracking for climate
monitoring (e.g. sensor battery voltage). Used when bringing a new Network
online, and (planned) run periodically to detect when a Data source's dataset
has changed.

### Databases and organization

**PCIC**:
Pacific Climate Impacts Consortium — the organization that operates crmprtd.

**PCDS**:
Pacific Climate Data Set — the shared database schema / data model that every
target database conforms to (the shape modeled by the `pycds` package). crmprtd
inserts into "PCDS-type" databases.

**CRMP**:
Both (1) the Climate Related Monitoring Program, BC's initiative to jointly pool
partner weather data, and (2) the production PCDS database covering BC.

**Metnorth**:
The production PCDS database covering the northern territories — Yukon (YT),
Northwest Territories (NT), and Nunavut (NU). Distinct from CRMP by geography and
by having different partners, institutions, and funding.

### Networks and sources

**Network**:
A distinct source of weather observations, identified by a name such as `ec`,
`moti`, or `bc_forestry`. Each Network has its own Download and Normalize logic
under `crmprtd/networks/<name>/` and maps one-to-one to a Network record in the
database.
_Avoid_: agency, provider, feed (when you mean the code-level source)

**Network record**:
The database row (pycds `Network`) representing the physical sensor network that
observations are attributed to. One-to-one with a Network.

**Network alias**:
A CLI convenience name that stands for one or more Networks run together in a
single pipeline invocation (e.g. `ytnt`, `bch`, `hourly_swobml2`).
_Avoid_: network group

**Data source**:
A remote resource, and the access methodology for it, that a Download phase
polls (e.g. the ECCC SWOB-ML partner feed, the EC datamart, the MoTI API). One
Data source can feed several Networks (the SWOB-ML feed supplies `bc_forestry`,
`bc_tran`, and others), but a Network never stitches together multiple Data
sources. Two Data sources may surface overlapping upstream data via different
methodologies (e.g. `ec` and `ec_swob` both reach Environment Canada data).
_Avoid_: feed, endpoint, resource, provider

### Observations and data flow

**Observation**:
A single measured value of one Variable at one Station at one time — the unit of
data the whole system acquires and stores. Exists in two representations on
either side of the Align phase: a Row before, an Obs after.

**Row**:
An Observation as emitted by the Normalize phase: a native-typed tuple
`(time, val, variable_name, unit, network_name, station_id, lat, lon)` with no
database identity, identifying its Station only by network-native id and
location.
_Avoid_: obs tuple, normalized observation

**Obs**:
An Observation after the Align phase: a pycds `Obs` object bound to real
database History and Variable rows, ready to Insert.

### Stations, histories, and variables

**Station**:
A set of weather-monitoring hardware, identified within its Network by a native
id (`Station.native_id`). crmprtd never invents this id; it matches or creates a
Station by the native id carried on a Row.

**native id**:
The identifier a Network assigns to a Station (`Station.native_id`), as opposed
to the database's surrogate key. It is what a Row carries to identify its
Station.

**History**:
A deployment of a Station's hardware at a specific location for a period of time
(bounded by `sdate`/`edate`), usually carrying the human-readable station name in
effect during that period. A Station accumulates a new History whenever it is
relocated or re-sited. The active History is the current one (`sdate` set,
`edate` null). Observations attach to a History, not directly to a Station.

**Variable**:
A measured quantity tracked for a Network (e.g. air temperature), matched
per-Network by name.
