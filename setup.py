import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = (0, 0, 11)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v', '--tb=no', 'tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="crmprtd",
    description="Utility to download Environment Canada MPO-XML and insert it into PCIC's database",
    keywords="sql database data science climate oceanography meteorology",
    version='.'.join(str(d) for d in __version__),
    url="http://www.pacificclimate.org/",
    author="James Hiebert",
    author_email="hiebert@uvic.ca",
    packages=find_packages(),
    scripts = ["scripts/real_time_ec.py",
               "scripts/fetch.py",
               "scripts/hourly_wmb.py",
               "scripts/wamr_hourly.py",
               "scripts/ec_recovery.py",
               "scripts/moti_hourly.py",
               "scripts/moti_infill_download.py",
               "scripts/moti_insert_files.py",
               "scripts/moti_infill_insert.py"
               ],
    package_data = {
        'crmprtd': ["data/*.yaml", "data/*.xsl"],
        },
    install_requires = ['lxml',
                        'psycopg2',
                        'pyyaml',
                        'python-dateutil',
                        'pytz',
                        'requests[security]',
                        'pycds >= 2.0.0',
                        'pint'
                        ],
    tests_require=['pytest',
                   'pysqlite'],
    cmdclass = {'test': PyTest},
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3 :: Only"]
    )
