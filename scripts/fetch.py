#!/usr/bin/env python

# Built-in libraries
import os
from urllib import urlretrieve
from optparse import OptionParser

# Locals
from ec_fetch import makeurl

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--province', dest='province',
                      help='2 letter province code')
    parser.add_option('-l', '--language', dest='language',
                      help="'e' (english) | 'f' (french)")
    parser.add_option('-f', '--frequency',
                      dest='frequency', help='daily|hourly')
    parser.add_option('-o', '--output_dir', dest='output_dir',
                      help='directory in which to put the downloaded file')
    parser.set_defaults(province='BC', language='e',
                        frequency='daily', output_dir='/tmp/ec_down/')
    (opts, args) = parser.parse_args()

    url = makeurl(opts.frequency, opts.province, opts.language)
    outfile = os.path.join(opts.output_dir, url['filename'])

    urlretrieve(url['url'], outfile)
