# News / Release Notes

## 3.1.2

*24-March-2020*

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
