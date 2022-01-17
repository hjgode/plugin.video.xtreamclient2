# -*- coding: utf-8 -*-
#for python2/3
# Module: context.xtreamdownload
#         cutils.py
# version 0.0.8
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from contextlib import closing
import sys
import json
import xbmc

def get_installed_version():
    """ Retrieve the currently installed version
    :return: currently installed version
    :rtype: dict
    """
    query = {
        "jsonrpc": "2.0",
        "method": "Application.GetProperties",
        "params": {
            "properties": ["version", "name"]
        },
        "id": 1
    }
    json_query = xbmc.executeJSONRPC(json.dumps(query))
    if sys.version_info[0] >= 3:
        json_query = str(json_query)
    else:
        json_query = unicode(json_query, 'utf-8', errors='ignore')  # pylint: disable=undefined-variable
    json_query = json.loads(json_query)
    version_installed = []
    if 'result' in json_query and 'version' in json_query['result']:
        version_installed = json_query['result']['version']
    return version_installed