# -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
#         database_update.py
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function
from datetime import date, datetime, timedelta

import os
import sys
import re

try:
  import xbmc
  print ("No Testing, running with xbmc")
  #from xtutils import start_connection, get_settings, get_url
  from xtutils import *
except Exception as e:
  print ("Testing environent, running without xbmc")
  from xtutils_test import start_connection, get_settings

from base64 import b64decode

class Simple_Epg:
  def __init__(self):
    self.myclient=None
    self.myclient=start_connection()

    pass

  def get_simple_epg(self, stream_id, archived_only=True):
    """ online, get epg data for stream id """
    data=self.myclient.get_simple_epg(stream_id)
    mylist=[]
    if isinstance(data['epg_listings'], list):
      for entry in data['epg_listings']:
        title=b64decode(entry['title'])# (entry['title'], title)
        description= b64decode(entry['description']) #, description)
        entry['title']=title
        entry['description']=description
        # do not add entries older than 30 hours
        # The above is handled by live_archive_database in function get_epgLast30()
        if not archived_only:
          mylist.append(entry)
        elif entry['has_archive']!=0:
          mylist.append(entry)
    return mylist
    pass # get_simple_epg

  pass # class