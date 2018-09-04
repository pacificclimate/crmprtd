# News / Release Notes

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
