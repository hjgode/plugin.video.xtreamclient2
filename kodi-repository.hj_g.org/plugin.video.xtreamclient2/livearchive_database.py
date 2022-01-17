# -*- coding: utf-8 -*-
#for python2
# Module: livearchive_database.py
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function
import datetime

import os
import sys

from database import QUERY_CLEANTABLE_LIVE_SQLITE, QUERY_CREATE_SQLITE
from xbmc import TRAY_CLOSED_MEDIA_PRESENT
try:
  import xbmc
except:
  #DEBUG
  xbmc=None
xbmc=None

import sqlite3

if sys.version_info[0] == 2:
    from _enum import Enum, unique
else:
    from enum import Enum, unique

"""
provide a database for use with live archive data
  tables:
    live_categories: 
      channel_name (category_name)
      channel_stream_id -> for timeshift playback and epg lookup
      channel_thumb 

      {u'category_id': u'83', u'category_name': u'DE \u2022 FullHD\u02b0\u1d49\u1d5b\u1d9c'}, 
      u'category_id': u'83', 
      u'epg_channel_id': u'DASERST', 
      u'name': u'Das Erste HD\u02b0\u1d49\u1d5b\u1d9c', 
      u'stream_id': 57221, 
      u'thumb': u'http://admin-serotv.com:8080/images/51e7682a87cfb0a577b3eb7123710739.png', 
      u'tv_archive': 1, 
      u'tv_archive_duration': 3, 
      u'video': u'http://<server>:<port>/play/v9OQ5ITy76wmBMEitt8VHiCyQUT5BLaKcmIAIf0V7CQXrdRjRhe2WvEcgGS3Iwrf/m3u8'

  epg_for_channel:
    channel_id (category_id) -> lookup category_name
    channel_stream_id
    title
    decription
    start
    end
    (duration?)
      {u'lang': u'de', 
      u'start_timestamp': 1641755701, 
      u'end': u'2022-01-09 21:15:01', 
      u'description': 'Die Sendereihe zeigt eine Zusammenfassung aller Spiele und Tore des aktuellen Spieltags.', 
      u'start': u'2022-01-09 20:15:01', 
      u'now_playing': 0, 
      u'title': 'Admiral BL: Alle Spiele, alle Tore', 
      u'epg_id': u'22', 
      u'channel_id': u'skysportaustria.at_1', 
      u'has_archive': 1, 
      u'id': 1641755700, 
      u'stop_timestamp': 1641759301}

"""
TABLEFIELDS_LIVE_CAT="(channel_name TEXT, channel_stream_id INT, thumb TEXT)"
INSERTVALUES_LIVE_CAT="(channel_name, channel_stream_id, thumb) VALUES (?,?,?) "
QUERY_INSERT_LIVE_CAT="INSERT OR REPLACE INTO live_categories " + INSERTVALUES_LIVE_CAT

QUERY_CREATETABLE_LIVE_CAT="CREATE TABLE IF NOT EXISTS live_categories " + TABLEFIELDS_LIVE_CAT
QUERY_CLEANTABLE_LIVE_CAT="DROP TABLE live_categories"
QUERY_GET_CHANNELS="SELECT * FROM live_categories"

TABLEFIELDS_EPG="(channel_stream_id INT, title TEXT, decription TEXT, start TEXT, end TEXT, duration TEXT)"
INSERTVALUES_EPG="(channel_stream_id, title, decription, start, end, duration) VALUES (?,?,?,?,?,?) "
QUERY_INSERT_EPG="INSERT OR REPLACE INTO epg_for_channel "+INSERTVALUES_EPG
QUERY_GET_EPG="SELECT * FROM epg_for_channel WHERE channel_stream_id="
QUERY_GET_EPG_LAST30="SELECT * FROM (select *,(strftime('%s','now')-strftime('%s', start))/3600 as DIFF from epg_for_channel WHERE channel_stream_id={}) WHERE DIFF<30"

QUERY_GET_MIN_MAX="select min(start) as first, max(start) as last from epg_for_channel"
QUERY_FIND_TITLE="SELECT * from epg_for_channel WHERE title LIKE "

QUERY_CREATETABLE_EPG="CREATE TABLE  IF NOT EXISTS epg_for_channel " + TABLEFIELDS_EPG
QUERY_CLEANTABLE_EPG="DROP TABLE epg_for_channel"

class EPG_Database:
  def __init__(self, addon_path):
    self.log("Database __init__ ...")
    self.dbpath=addon_path
    self.db_file=os.path.join(self.dbpath, "epgdatabase.sqlite")
    self.sqlcon_wl=None
    self.sqlcursor_wl=None
    self._connect_db()
    self.log("database connected")
    pass

  def _init_tables(self):
    self.log("_init_tables...")
    if self.sqlcursor_wl==None:
      self._connect_db()
    self._drop_tables()
    self._create_tables

  def _drop_tables(self):
    self.log("_drop_tables...")
    if self.sqlcursor_wl==None:
      self.execute(QUERY_CLEANTABLE_LIVE_CAT,commit=True)
      self.execute(QUERY_CLEANTABLE_EPG,commit=True)
    pass

  def _connect_db(self):
    self.log("_connect_db()...")
    try:
      self.sqlcon_wl = sqlite3.connect(self.db_file)
      if not os.path.exists(self.db_file):
        self._create_tables()
      self.sqlcursor_wl = self.sqlcon_wl.cursor()
      # create tables if they don't exist
      self._create_tables()
#      self.sqlcursor_wl.execute(QUERY_CREATE_MV_SQLITE)
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
    except SystemExit:
        return 1
    except BaseException:
        self.log(u"Error while opening %s: %s" % (self.db_file, sys.exc_info()[2]))
        self._close_db()
        return 1
    # only commit the changes if no error occured to ensure database persistence
    if(self.sqlcon_wl):
      self.log("db commit()...")
      self.sqlcon_wl.commit()
    else:
      self.log ("_connect() FAILED")
    return self.sqlcursor_wl

  def _create_tables(self):
    self.log("create tables...")
    self.execute(QUERY_CREATETABLE_LIVE_CAT,commit=True)
    self.execute(QUERY_CREATETABLE_EPG,commit=True)
    pass

  def cleanTableEPG(self):
    self.log("create table...")
    if self.sqlcon_wl:
      self.execute(QUERY_CLEANTABLE_EPG,commit=True)
      self._create_tables()
    pass

  def cleanTableLIVE(self):
    self.log("create table...")
    if self.sqlcon_wl:
      self.execute(QUERY_CLEANTABLE_LIVE_CAT,commit=True)
      self._create_tables()
    pass

  def get_first_last(self):
    (first, last)=self.execute((QUERY_GET_MIN_MAX), single=True)
    return (first, last)
    pass

  def find(self, findstr):
    query=(QUERY_FIND_TITLE + "'%"+findstr+"%'")
    mylist = self.execute((query), single=False)
    return mylist
    pass
  
  def get_channels(self):
    mylist=[]
    data=self.execute(QUERY_GET_CHANNELS)
    for row in data:
      mylist.append({"channel_name":row[0], "channel_stream_id":row[1], "thumb":row[2]})
    return mylist
    pass

  def addChannel(self, channel_name, channel_stream_id, thumb):
    """
      channel_name (category_name)
      channel_stream_id -> for timeshift playback and EPG lookup
      thumb: image
    """
    #items="('"+channel_name+ "', " +str(channel_stream_id)+ ",'" +thumb+ "')"
    items=((channel_name, channel_stream_id, thumb))
    self.execute(QUERY_INSERT_LIVE_CAT,args= items, single=True, commit=True)
    pass

  def get_epgLast30(self, channel_stream_id):
    """
      returns:
        epg['channel_stream_id']=channel_stream_id
        epg['title']=row[0]
        epg['description']=row[1]
        epg['start']=row[2]
        epg['end']=row[3]
        epg['duration']=row[4]
    """
    heute=datetime.datetime.now()
    query=((QUERY_GET_EPG + str(channel_stream_id)))
    query=((QUERY_GET_EPG_LAST30.format(channel_stream_id)))

    rows=self.execute(query, single=False)
    mylist=[]
    for row in rows:
      # 0                  1      2           3      4    5
      # channel_stream_id, title, decription, start, end, duration
      epg={}
      epg['channel_stream_id']=channel_stream_id
      epg['title']=row[1]
      epg['description']=row[2]
      epg['start']=row[3]
      epg['end']=row[4]
      epg['duration']=row[5]
      # http://ip:port/streaming/timeshift.php?username=X&password=X&stream=X&start=2016-03-19:16-00&duration=120

      # the archive is hold for 3 (by 10 hours?)
      # do not add epg_info for older entries
      ## SELECT * FROM (select *,(strftime('%s','now')-strftime('%s', start))/3600 as DIFF from epg_for_channel WHERE channel_stream_id=57221) WHERE DIFF<30

      """
      date_format_string="%Y-%m-%d %H:%M:%S" # 2022-01-08 20:15:00
      start=datetime.strptime(epg['start'], date_format_string)
      diff=heute-start
      diff_in_hours = diff.total_seconds() / 3600
      if diff_in_hours<30:
      """
      mylist.append(epg)
    return mylist      
    pass

  def add_epg(self, channel_stream_id, epg_infos):
    """ add a list of epg entries """
    items=[] # epg_infos
    #we need only 
    # INSERTVALUES_EPG="INSERT INTO epg_for_channel (channel_stream_id, title, decription, start, end, duration) VALUES (?,?,?,?,?,?,?) "
    for epg in epg_infos:
      duration=int ((epg['stop_timestamp']-epg['start_timestamp'])/60) # 13020 seconds => 217 minutes for start=u'2022-01-08 11:53:00' and end=u'2022-01-08 15:30:00'
      title=epg['title'].decode('utf-8')
      description=epg['description'].decode('utf-8')
      item=((channel_stream_id, title, description, epg['start'], epg['end'], duration))
      items.append(item)

    try:
      if self.sqlcon_wl:
        item=(items)
        c = self.sqlcursor_wl.executemany(QUERY_INSERT_EPG,item) #TODO: add data
        self.sqlcon_wl.commit()
        return c.rowcount # self.sqlcursor_wl.lastrowid
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
      return -1
    except SystemExit:
        return -1
    except BaseException:
        self.log(u"Error while opening %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self._close_db()
        return -1

    pass

  def addManyChannels(self, datalist):
    """ add many channels 
        Arguments:
        datalist:list [(channel_name, channel_id, channel_stream_id),...]
    """
    try:
      if self.sqlcon_wl:
        item=(datalist)
        c = self.sqlcursor_wl.executemany(QUERY_INSERT_LIVE_CAT,item) #TODO: add data
        self.sqlcon_wl.commit()
        return c.rowcount # self.sqlcursor_wl.lastrowid
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
      return -1
    except SystemExit:
        return -1
    except BaseException:
        self.log(u"Error while opening %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self._close_db()
        return -1
    

  def execute(self, tuple, single = False, args = {}, commit = False):
    """ sql = ("SELECT word FROM word_blacklist")
        results = execute(sql)
    """
    try:
      self.sqlcursor_wl.execute(tuple, args)

      if commit == True:
          self.sqlcon_wl.commit()
      else:
          if single == True:
              return self.sqlcursor_wl.fetchone()
          else:
              return self.sqlcursor_wl.fetchall()
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
      return None
    except SystemExit:
        return None
    except BaseException:
        self.log(u"Error with execute %s: %s" % (self.db_file, sys.exc_info()[2]))
        self._close_db()
        return None

  def _close_db(self):
    if self.sqlcon_wl:
      self.sqlcon_wl.commit()
      self.sqlcon_wl.close()
      self.sqlcon_wl = 0
      self.log("db closed")

  def log(self, s):
    if xbmc!=None:
      xbmc.log("epg database xtreamdownload: " + s, xbmc.LOGNOTICE)
    else:
      print("epg database xtreamdownload: " + s)
