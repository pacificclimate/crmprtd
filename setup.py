import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from crmprtd import NETWORKS

__version__ = (4, 0, 0)


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
        "execution/bch_newdb.sh",
        "execution/bch.sh",
        "execution/crd_newdb.sh",
        "execution/crd.sh",
        "execution/crmprtd_inserts.sh",
        "execution/ec_db.sh",
        "execution/ec_newdb.sh",
        "execution/ec.sh",
        "execution/hourly_swobml2_newdb.sh",
        "execution/hourly_swobml2.sh",
        "execution/hourly_swobml_db.sh",
        "execution/hourly_swobml.sh",
        "execution/metnorth.sh",
        "execution/moti_newdb.sh",
        "execution/moti.sh",
        "execution/update_matviews_lazy.sql",
        "execution/wamr_backpatch_20201118.sh",
        "execution/wamr_db.sh",
        "execution/wamr_newdb.sh",
        "execution/wamr.sh",
        "execution/wmb_newdb.sh",
        "execution/wmb.sh",
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
        "crmprtd": [
            "data/*.yaml",
            "data/*.xsl",
            "tests/data/*",
            "wamr/station_substitutions.yaml",
        ],
    },
    install_requires=[
        "lxml",
        "psycopg2",
        "pyyaml",
        "python-dateutil",
        "pytz",
        "requests[security]",
        "pycds==4.*",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
