import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from crmprtd import NETWORKS

__version__ = (3, 2, 2)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["-v", "--tb=no", "tests"]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="crmprtd",
    description=(
        "Utility to download Environment Canada MPO-XML and insert"
        "it into PCIC's database"
    ),
    keywords="sql database data science climate oceanography meteorology",
    version=".".join(str(d) for d in __version__),
    url="http://www.pacificclimate.org/",
    author="James Hiebert",
    author_email="hiebert@uvic.ca",
    packages=find_packages(exclude=("speed_test",)),
    scripts=[
        "scripts/ec_recovery.py",
        "scripts/moti_infill_download.py",
        "scripts/moti_insert_files.py",
        "scripts/moti_infill_insert.py",
    ],
    entry_points={
        "console_scripts": [
            "crmprtd_process=crmprtd.process:main",
            "crmprtd_infill_all=scripts.infill_all:main",
        ]
        + [
            f"download_{network}=crmprtd.{network}.download:main"
            for network in NETWORKS
        ]
    },
    package_data={
        "crmprtd": ["data/*.yaml", "data/*.xsl", "tests/data/*"],
    },
    install_requires=[
        "lxml",
        "psycopg2",
        "pyyaml",
        "python-dateutil",
        "pytz",
        "requests[security]",
        "pycds >= 2.0.0",
        "pint",
        "pysftp",
    ],
    tests_require=["pytest", "pysqlite" "requests_mock"],
    extras_require={
        "jsonlogger": "python-json-logger",
    },
    cmdclass={"test": PyTest},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
