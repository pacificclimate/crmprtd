import sys


if sys.version_info.major < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
