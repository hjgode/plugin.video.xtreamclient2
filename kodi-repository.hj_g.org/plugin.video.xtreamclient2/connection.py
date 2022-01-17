# -*- coding: utf-8 -*-
import re
import sys

if sys.version_info[0] == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

"""
#another Python2/3 approach
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

try:
    pythonVer = sys.version_info.major
except:
    pythonVer = 2
"""

class Connection:
    def __init__(self, scheme = "http", server = "", port = 80, username = "", password = ""):
        self.scheme = scheme
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def __repr__(self):
        string ="{} {}://{}:{}?username={}&password={}".format(self.__class__, self.scheme, self.server, self.port, self.username, self.password)
        return string # f"{self.__class__} {self.scheme}://{self.server}:{self.port}?username={self.username}&password={self.password}"

    def __str__(self):
        port = ":{}".format(self.port) if self.port else ""
        string="{}://{}{}?username={}&password={}".format(self.scheme, self.server, port, self.username, self.password)
        return string # f"{self.scheme}://{self.server}{port}?username={self.username}&password={self.password}"

    @classmethod
    def from_url(cls, url):
        o = urlparse(url)
        regexp_url = r"^username=(?P<username>\w+)&password=(?P<password>\w+)"
        res = re.match(regexp_url, o.query, re.IGNORECASE)
        return (
            (True, cls(server=o.hostname, port=o.port, scheme=o.scheme, **res.groupdict())) if res else (False, cls())
        )
