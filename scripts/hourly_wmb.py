#!/usr/bin/env python

# From Jim Colley <Jim.Colley@gov.bc.ca>
# "The first file contains a rolling 24hrs of data for each station, and is
# updated at approximately 00:35 past each hour"
#
# FIXME: Replace opts.log with native python logging configuration
# FIMXE: Replace email_error with using a logging handler to catch critical
# errors (i.e. logger.critical()) and do the email

from pkg_resources import resource_stream
from argparse import ArgumentParser

# Local
from crmprtd.wmb.download import run


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-L', '--log_conf',
                        default=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log',
                        default=None,
                        help='Override the default log filename')
    parser.add_argument('-e', '--error_email',
                        default=None,
                        help=('Override the default e-mail address to which '
                              'the program should report critical errors'))
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help=('Set log level: DEBUG, INFO, WARNING, ERROR, '
                              'CRITICAL.  Note that debug output by default '
                              'goes directly to file'))
    parser.add_argument('-f', '--ftp_server',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'server'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    parser.add_argument('--auth',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key',
                        help=("Top level key which user/pass are stored in "
                              "yaml file."))
    parser.add_argument('--username',
                        help=("The username for data requests. Overrides auth "
                              "file."))
    parser.add_argument('--password',
                        help=("The password for data requests. Overrides auth "
                              "file."))
    parser.add_argument('-C', '--cache_dir',
                        help='Directory in which to put the downloaded file')
    parser.add_argument('-a', '--archive_dir',
                        help=('Directory in which to put data that could not '
                              'be added to the database'))
    parser.add_argument('-A', '--archive_file',
                        default=None,
                        help=('An archive file to parse INSTEAD OF '
                              'downloading from ftp. Can be a local reference '
                              'in the archive_dir or absolute file path'))
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")

    args = parser.parse_args()
    run(args)
