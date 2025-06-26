# News / Release Notes

## 5.0.2

_2025-Jun-26_

ECCC added a new server with longer data retention (90 vs 30 days),
and subtly changed the directory structure on their legacy server
dd.weather.gc.ca. This short patch fixes that for both ECCC native
data as well as the partner SWOB-ML data that comes through ECCC.

## 5.0.1

_2025-Jun-23_

Fixed the PyPI publishing workflow to use a supported version of
Python and to match release candidate versions

## 5.0.0

_2025-Jun-19_

Maintenance updates:

- Upgrade pyproject.toml to be PEP 621-compliant
- Change supported python versions to 3.9-3.12 and address all
  deprecations
- Upgrade to SQLAlchemy 2.x

## 4.7.0

_2024-Apr-29_

Adds an alternate process pipeline, `crmprtd_gulpy` to the package

## 4.6.0

_2024-Mar-26_

[Add provinces argument to download_pipeline](https://github.com/pacificclimate/crmprtd/pull/179)

## 4.5.0

_2024-Jan-18_

Compatible with database revision 879f0efa125f (PyCDS 4.3.0).

- Adds feed for RioTinto network via ECCC DataMart
- Improves BC Hydro testing
- Improves testing and usability of the process() function

## 4.4.0

_2023-May-11_

Compatible with database revision 879f0efa125f (PyCDS 4.3.0).

The big news is:
- ~100x improvement in speed in process phase
- Now using Poetry to manage dependencies etc. No more Pipenv!

- [Fix download phase crash](https://github.com/pacificclimate/crmprtd/pull/170)
- [Improve align and insert phase performance](https://github.com/pacificclimate/crmprtd/pull/168)
- [Convert to Poetry](https://github.com/pacificclimate/crmprtd/pull/161)
- [Catch and log all errors](https://github.com/pacificclimate/crmprtd/pull/159)

## 4.3.1

_2023-Apr-19_

Compatible with database revision 879f0efa125f (PyCDS 4.3.0).

- [Completes BC Hydro data feed support](https://github.com/pacificclimate/crmprtd/pull/158)

## 4.3.0

_2023-Apr-05_

Compatible with database revision 879f0efa125f (PyCDS 4.3.0).

Upgrades to PyCDS 4.3.0, which installs script `manage-scripts`.

- [Upgrade to pycds ~= 4.3](https://github.com/pacificclimate/crmprtd/pull/153)

## 4.2.1

_2023-Feb-24_

Compatible with database revision 879f0efa125f (PyCDS 4.0.0).

This version has been tested in the field targeting the CRMP2 database.

PRs:
- [Fix WAMR normalization](https://github.com/pacificclimate/crmprtd/pull/150)

## 4.2.0

_2023-Feb-02_

Compatible with database revision 879f0efa125f (PyCDS 4.0.0).

This version has been tested in the field targeting the Metnorth2 database.

PRs:

- [Fix problems for actual use #142](https://github.com/pacificclimate/crmprtd/pull/142)
- [Convert to pyproject.toml #140](https://github.com/pacificclimate/crmprtd/pull/140)
- [Fix version arg bug #138](https://github.com/pacificclimate/crmprtd/pull/138)

## 4.1.0

_2023-Jan-20_

Compatible with database revision 879f0efa125f (PyCDS 4.0.0).

This revision adds two new scripts, `crmp_download` and `crmp_pipeline`, which,
respectively, dispatch download and download-cache-process operations to the 
appropriate network-specific methods according to the `-N/--network` argument 
they both take.

Script `crmp_download` replaces individual invocations of 
`download -N <network>` scripts and the dynamic console scripts set up in 
`setup.py` associated with them.

Script `crmp_pipeline` replaces the collection of invocation shell scripts
that were previously in use.

All other changes are either non-functional or are superseded by later changes
in this release.

PRs:
- [Replace execution shell scripts with a Python script](https://github.com/pacificclimate/crmprtd/pull/134)
- [Fix arg parsing](https://github.com/pacificclimate/crmprtd/pull/133)
- [Move network-specific code into new module crmprtd.networks](https://github.com/pacificclimate/crmprtd/pull/131)
- [Replace `download_<network>` scripts with a `download -N <network>` script](https://github.com/pacificclimate/crmprtd/pull/128)
- [Support multiple target databases](https://github.com/pacificclimate/crmprtd/pull/126)
- [Bring execution scripts under change control](https://github.com/pacificclimate/crmprtd/pull/124)
 
## 4.0.0

*16-Dec-2022*

Major change is to upgrade PyCDS to ver 4.0.0, which makes this release 
compatible with revision 879f0efa125f of the database.

Changes:
- [Use distance ordering in spatially matched histories](https://github.com/pacificclimate/crmprtd/pull/122)
- [Add --version arg to console scripts](https://github.com/pacificclimate/crmprtd/pull/121)
- [More pipenv improvements](https://github.com/pacificclimate/crmprtd/pull/119)
- [Upgrade PyCDS to ver 4.0.0](https://github.com/pacificclimate/crmprtd/pull/116)
- [Don't use psycopg2-binary](https://github.com/pacificclimate/crmprtd/pull/113)
- [Improve installation instructions](https://github.com/pacificclimate/crmprtd/pull/112)
- [Remove errors from Pipfile](https://github.com/pacificclimate/crmprtd/pull/109)

## 3.5.1

*27-June-2022*

* Fixed bug where improper dependency broke the insertion of stations
  on demand.

## 3.5.0

*24-June-2022*

* Implements optional time range selection to process script for a
  pre-filter before insertion

## 3.4.0

*22-June-2022*

* Adds support for several new networks from ECCC DataMart
  * Yukon Avalanche
  * Yukon Fire Weather
  * DFO Lighthouses
* Adds new optional "infer" phase to the pipeline to detect missing
  metadata based on a set of observations
* Standardizes time arguments across all download scripts

## 3.3.0

*14-April-2022*

* Adds support for Northwest Territories and Yukon Territories feeds
  from ECCC DataMart
* Converts project setup to use pipenv

## 3.2.4

*28-May-2021*

* Reassociates certain mvan stations that come from WAMR

## 3.2.3

*19-April-2021*

* Parametrize's MoTI download URL
* Corrects problem in installer (GH Issue #91)

## 3.2.2

*02-December-2020*

* Fixes bug where bc_tran download script was omitted from the build

## 3.2.1

*26-November-2020*

* Fixes bug were BC Hydro didn't have its module initialized

## 3.2.0

*26-November-2020*

* Handles a few aliases for data values from WAMR/MoE-ENV (GH Issue #88)
* Adds download module for BC Hydro data (GH Issue #81)
* Updates and parameterizes deprecated EC URL (GH Issue #85)
* Improvements to testing and code formattign (GH Issues #74 #84)

## 3.1.5

*03-September-2020*

* Handles temperature units from the CRD

## 3.1.4

*26-August-2020*

* Standardizes the interface between the download and normalize phases (GH Issue #75)

## 3.1.3

*15-July-2020*

* Handles new (and different) fields in the WAMR stream

## 3.1.2

*30-June-2020*

* Updates continuous integration tooling
* Adds more robust check for empty data

## 3.1.1

*24-March-2020*

* Fixes continuous integration issue

## 3.1.0

*24-March-2020*

* Adds new network support for the Capital Regional District (CRD)
* Logs network name to data insertion log entries
* Adds a globally usable infilling script that infills each network between
  an arbitrary time range
* Fixes date formatting in download_moti HTTP parameters (GH Issue #58)

## 3.0.0

*08-January-2020*

* Drops support for Python 3.5
* Demotes faux-observations with value "MSNG" to log level DEBUG
* Makes timezone handling consistent across all normalize modules
* Corrects time range selection in the download_moti script
* Documents difference in time selection for each network's download script

## 2.0.3

*19-December-2019*

* Fixes mistake in WAMR units (the author mistook "Deg." for
  temperature degrees when it's actually wind direction degrees
  (unitless)

## 2.0.2

*19-December-2019*

* Moves WAMR's "celsius" aliases into align to be handled by pint

## 2.0.1

*10-December-2019*

* Adds extra "celsius" aliases for units conversion
* Adds an install option to log in JSON format

## 2.0.0

*27-November-2019*

* Adds four new network feeds via an Environment Canada XML partner feed
* Adds full use of diagnostic (no database commit) mode
* Drops support for Python 3.4
* Adds support for Python 3.7

## 1.0.1

*04-September-2018*

* Makes logs less noisy by demoting duplicate obs (insert phase) from
  warning level to debug and demoting untracked variables (align
  phase) from warning to debug.

## 1.0.0
*29-August-2018*

* Complete refactor of entire code base.
* Execution of pipeline has been restructured.
    * download.py (for each network) can be called directly.
    * download.py output can be piped to a file or to process.py.
    * process.py handles the final 3 stages of data pipeline (normalize, align, insert).

## 0.3.0

*12-August-2018*

* Consolidated code that sets up and configures logging so that usage is the same across the various modules.

## 0.2.0

*02-August-2018*

* Standardized logging across all modules and added the option for JSON output.
* Added test coverage testing and code linting to continuous integration.
* Fixed a bug where non-duplicate observations occurring before a duplicate were being discarded.
* Removed dependency on in-database code making the code robust against [issue 8](https://github.com/pacificclimate/crmprtd/issues/8).
