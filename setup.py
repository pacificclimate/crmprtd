import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = (3, 1, 4)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v', '--tb=no', 'tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="crmprtd",
    description=("Utility to download Environment Canada MPO-XML and insert"
                 "it into PCIC's database"),
    keywords="sql database data science climate oceanography meteorology",
    version='.'.join(str(d) for d in __version__),
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
        'console_scripts': [
            'download_bch=crmprtd.bch.download:main',
            'download_bc_env_snow=crmprtd.bc_env_snow.download:main',
            'download_bc_env_aq=crmprtd.bc_env_aq.download:main',
            'download_bc_forestry=crmprtd.bc_forestry.download:main',
            'download_bc_tran=crmprtd.bc_tran.download:main',
            'download_crd=crmprtd.crd.download:main',
            'download_ec=crmprtd.ec.download:main',
            'download_moti=crmprtd.moti.download:main',
            'download_wamr=crmprtd.wamr.download:main',
            'download_wmb=crmprtd.wmb.download:main',
            'crmprtd_process=crmprtd.process:main',
            'crmprtd_infill_all=scripts.infill_all:main'
        ]
    },
    package_data={
        'crmprtd': ["data/*.yaml", "data/*.xsl"],
    },
    install_requires=['lxml',
                      'psycopg2',
                      'pyyaml',
                      'python-dateutil',
                      'pytz',
                      'requests[security]',
                      'pycds >= 2.0.0',
                      'pint'
                      ],
    tests_require=['pytest',
                   'pysqlite'
                   'requests_mock'],
    extras_require={
        'jsonlogger': 'python-json-logger',
    },
    cmdclass={'test': PyTest},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ]
)
