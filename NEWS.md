# News / Release Notes

## 0.3.0

*12-August-2018*

* Consolidated code that sets up and configures logging so that usage is the same across the various modules.

## 0.2.0

*02-August-2018*

* Standardized logging across all modules and added the option for JSON output.
* Added test coverage testing and code linting to continuous integration.
* Fixed a bug where non-duplicate observations occurring before a duplicate were being discarded.
* Removed dependency on in-database code making the code robust against [issue 8](https://github.com/pacificclimate/crmprtd/issues/8).
