import sys

if sys.version_info.major < 3:
    from urlparse import urlparse
    from lxml.etree import fromstring
else:
    from urllib.parse import urlparse
    import lxml.etree
    def fromstring(s):
        return lxml.etree.fromstring(bytes(s, encoding='utf-8'))
