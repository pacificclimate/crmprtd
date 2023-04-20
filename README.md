# crmprtd

TODO: Update crontab in Usage

![Python CI](https://github.com/pacificclimate/crmprtd/workflows/Python%20CI/badge.svg?branch=master)
![Pypi Publishing](https://github.com/pacificclimate/crmprtd/workflows/Pypi%20Publishing/badge.svg?branch=master)

Utility to download near real time weather data and insert it into PCIC 
PCDS-type databases (e.g., CRMP, Metnorth).

## Documentation

- Installation
  - [System-level dependencies](docs/installation/system-deps.md) 
  - [For production](docs/installation/production.md)
  - [For development](docs/installation/development.md)
- [Usage (CLI)](docs/usage.md)
- Development
  - [Caveats](docs/development/caveats.md)
  - [Unit tests](docs/development/unit-tests.md)

## Creating a production release

1. Modify `project.version` in `pyproject.toml`: First remove any suffix
   to the version number, as our convention is to reserve those for test builds
   (e.g., `1.2.3` is a release build, `1.2.3.dev7` is a test build).
   Then increment the release build version.
1. Summarize release changes in `NEWS.md`
1. Commit these changes, then tag the release
   ```bash
   git add pyproject.toml NEWS.md
   git commit -m"Bump to version X.Y.Z"
   git tag -a -m"X.Y.Z" X.Y.Z
   git push --follow-tags
   ```
1. Our GitHub Actions [workflow](https://github.com/pacificclimate/crmprtd/blob/i71-action-best-practices/.github/workflows/python-ci.yml) will build and release the package on our PyPI server.


## Creating a dev/test release

The process is very similar to a production release, but uses a different
version number convention, and omits any notice in NEWS.md.

1. Modify `project.version` in `pyproject.toml`: Add or increment the suffix 
   in the pattern `.devN`, where N is any number of numeric digits (e.g., `1.2.3.dev11`).
   Our convention is to reserve those for test releases
   (e.g., `1.2.3` is a release build, `1.2.3.dev11` is a test build). 
2. Commit changes and tag the release:
   ```bash
   git add pyproject.toml
   git commit -m"Create test version X.Y.Z.devN"
   git tag -a -m"X.Y.Z.devN" X.Y.Z.devN
   git push --follow-tags
   ```
1. Our GitHub Actions [workflow](https://github.com/pacificclimate/crmprtd/blob/i71-action-best-practices/.github/workflows/python-ci.yml) will build and release the package on our PyPI server.

