import csv
import os

from datetime import datetime

# Local
from crmprtd.wamr import setup_logging, FTPReader
from crmprtd.wamr.normalize import prepare, normalize_file, normalize_ftp


def run(args):
    # Logging
    log = setup_logging(args.log_level, args.log, args.error_email)
    log.info('Starting WAMR rtd')

    # Output files
    if args.error_file:
        error_file = open(args.error_file, 'a')
    else:
        error_filename = 'wamr_errors_{}.csv'.format(datetime.strftime(
            datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        error_file = open(os.path.join(args.cache_dir, error_filename), 'a')

    if args.input_file:
        log.info('Nomalizing File Data')
        normalize_file(args, error_file, log)
    else:
        # FTP
        # rows, fieldnames = ftp2rows(args.ftp_server, args.ftp_dir, log)
        ftpreader = ftp2rows(args.ftp_server, args.ftp_dir, log)
        normalize_ftp(ftpreader, error_file, args, log)

        # if not args.cache_file:
        #     args.cache_file = 'wamr_download_{}.csv'.format(datetime.strftime(
        #         datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        # with open(args.cache_file, 'w') as cache_file:
        #     cache_rows(cache_file, rows, fieldnames)

    # log.info('observations read into memory', extra={'num_obs': len(rows)})
    # prepare(rows, error_file, log, args)


def cache_rows(file_, rows, fieldnames):
    copier = csv.DictWriter(file_, fieldnames=fieldnames)
    copier.writeheader()
    copier.writerows(rows)


def ftp2rows(host, path, log):
    log.info('Fetching file from FTP')
    log.info('Listing {}/{}'.format(host, path))

    try:
        ftpreader = FTPReader(host, None,
                              None, path, log)
        log.info('Opened a connection to {}'.format(host))
        # reader = ftpreader.csv_reader(log)
        # log.info('instantiated the reader and downloaded all of the data')
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    # return [row for row in reader], reader.fieldnames
    return ftpreader
