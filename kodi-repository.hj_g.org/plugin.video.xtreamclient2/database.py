# -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
#         database.py
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function

import os
import sys
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

@unique
class DataType(Enum):
  live=0
  series=1
  vod=2
  pass

# CHANGED: renamed episode to thumb to provide a thumbnail image for ListItem
#                   0        1          2                   3               4           5               6           7
TABLEFIELDS = "(typ INT, name TEXT, categoryID TEXT, categoryName TEXT, stream TEXT, seriesID TEXT, thumb TEXT, thumb TEXT)"
# the above has a rowid field!

INSERTVALUES = "(typ, name, categoryID, categoryName, stream, seriesID, season, thumb) VALUES (?,?,?,?,?,?,?,?)"


"""
create a database for live, series and vod
  TABLE
    typ:str  live|series|vod using enum lookup
    name:str  name or title
    categoryID:str  category ID
    stream:str  direct_source or video stream URL
    seriesID:str  series ID or None
      season:str season number for series or None
      episode:str episode name for series or None

      GET Live Stream Categories
      player_api.php?username=X&password=X&action=get_live_categories
        GET LIVE Streams
        player_api.php?username=X&password=X&action=get_live_streams (This will get All LIVE Streams)
        player_api.php?username=X&password=X&action=get_live_streams&category_id=X (This will get All LIVE Streams in the selected category ONLY)

      GET VOD Stream Categories
      player_api.php?username=X&password=X&action=get_vod_categories
        GET VOD Streams
        player_api.php?username=X&password=X&action=get_vod_streams (This will get All VOD Streams)
        player_api.php?username=X&password=X&action=get_vod_streams&category_id=X (This will get All VOD Streams in the selected category ONLY)
          GET VOD Info
          player_api.php?username=X&password=X&action=get_vod_info&vod_id=X (This will get info such as video codecs, duration, description, directors for 1 VOD)

      GET SERIES Categories
      player_api.php?username=X&password=X&action=get_series_categories
        GET SERIES Streams
        player_api.php?username=X&password=X&action=get_series (This will get All Series)
        player_api.php?username=X&password=X&action=get_series&category_id=X (This will get All Series in the selected category ONLY)
          GET SERIES Info
          player_api.php?username=X&password=X&action=get_series_info&series_id=X

"""

QUERY_CREATE_SQLITE = "CREATE TABLE IF NOT EXISTS xtreamdatabase "+ TABLEFIELDS
QUERY_INSERT_SQLITE = 'INSERT OR REPLACE INTO xtreamdatabase '+ INSERTVALUES
#QUERY_MV_UPDATE_SQLITE = 'UPDATE xtreamdatabase SET playCount = ?, lastplayed = ?, lastChange = ? WHERE idMovieImdb LIKE ?'
QUERY_REMOVE_SQLITE = "DELETE FROM xtreamdatabase WHERE stream = '{}';"

QUERY_ALL_WHERE_LIKE_SQLITE = "SELECT * from xtreamdatabase WHERE name LIKE "
QUERY_LIVE_WHERE_LIKE_SQLITE = "SELECT * from xtreamdatabase WHERE typ=0 AND name LIKE "
QUERY_SERIES_WHERE_LIKE_SQLITE = "SELECT * from xtreamdatabase WHERE typ=1 AND name LIKE "
QUERY_VOD_WHERE_LIKE_SQLITE = "SELECT * from xtreamdatabase WHERE typ=2 AND name LIKE "

QUERY_CLEAR_SQLITE = "DELETE FROM xtreamdatabase;"

QUERY_CLEANTABLE_LIVE_SQLITE = "DELETE FROM xtreamdatabase where typ=0;"
QUERY_CLEANTABLE_SERIES_SQLITE = "DELETE FROM xtreamdatabase where typ=1;"
QUERY_CLEANTABLE_VOD_SQLITE = "DELETE FROM xtreamdatabase where typ=2;"

QUERY_DROPTABLE_SQLITE = "DROP TABLE xtreamdatabase;"
QUERY_LIST_SQLITE = "select * from xtreamdatabase"

QUERY_RENAME_EPISODE_TO_THUMB = "ALTER TABLE xtreamdatabase RENAME COLUMN episode TO thumb"

class Database:
  def __init__(self, addon_path):
    self.log("Database __init__ ...")
    self.dbpath=addon_path
    self.db_file=os.path.join(self.dbpath, "xtreamdatabase.sqlite")
    self.sqlcon_wl=None
    self.sqlcursor_wl=None
    self._connect_db()
    self.log("database connected")
    pass

  def _init_table(self):
    self.log("_init_table...")
    if self.sqlcursor_wl==None:
      self._connect_db()
    self._drop_table()
    self._create_table()

  def _connect_db(self):
    self.log("_connect_db()...")
    try:
      self.sqlcon_wl = sqlite3.connect(self.db_file)
      self.sqlcursor_wl = self.sqlcon_wl.cursor()
      # create tables if they don't exist
      self._create_table()
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
        self.log(u"Error while opening %s: %s" % (self.db_file, sys.exc_info()[2]), xbmc.LOGERROR)
        self.close_db(3)
        return 1
    # only commit the changes if no error occured to ensure database persistence
    if(self.sqlcon_wl):
      self.log("db commit()...")
      self.sqlcon_wl.commit()
    else:
      self.log ("_connect() FAILED")
    return self.sqlcursor_wl
    pass


  def find(self, findstr, typ=None):
    if self.sqlcon_wl:
      if typ==None:
        #search all
        query=(QUERY_ALL_WHERE_LIKE_SQLITE + "'%"+findstr+"%'")
      elif typ==0:
        query=(QUERY_LIVE_WHERE_LIKE_SQLITE + "'%"+findstr+"%'")
      elif typ==1:
        query=(QUERY_SERIES_WHERE_LIKE_SQLITE + "'%"+findstr+"%'")
      elif typ==2:
        query=(QUERY_VOD_WHERE_LIKE_SQLITE + "'%"+findstr+"%'")
      else:
        query=(QUERY_ALL_WHERE_LIKE_SQLITE + "'%"+findstr+"%'")
      myresult=self.execute(query, single=False, commit=False)
      return myresult
      """
      #myresult=self._doExecute(query)
      #return myresult
      self.sqlcursor_wl.execute(query) #TODO: add data
      myresult=self.sqlcursor_wl.fetchall()
      return myresult # self.sqlcursor_wl.lastrowid
      """
    pass

  def add_many(self, datalist):
    """ data list must be 
    [ (typ, name, categoryID, categoryName, stream, seriesID="", season="", thumb=""), ...] 
    """
    try:
      if self.sqlcon_wl:
        item=(datalist)
        c = self.sqlcursor_wl.executemany(QUERY_INSERT_SQLITE,item) #TODO: add data
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

  def add_item(self, typ, name, categoryID, categoryName, stream, seriesID="", season="", thumb=""):
    self.log("add item: " + name + "\n" +stream)
    if typ=="live":
      itype=DataType.live
    elif typ=="vod":
      itype=DataType.vod
    elif typ=='series':
      itype=DataType.series
    else:
      return -1

    try:
      if self.sqlcon_wl:
        item=(typ, name, categoryID, categoryName, stream, seriesID, season, thumb)
        rowid = self.sqlcursor_wl.execute(QUERY_INSERT_SQLITE,item) #TODO: add data
        self.sqlcon_wl.commit()
        return rowid # self.sqlcursor_wl.lastrowid
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

  def _create_table(self):
    self.log("create table...")

    self.sqlcursor_wl.execute(QUERY_CREATE_SQLITE)
    try:
      self.execute((QUERY_RENAME_EPISODE_TO_THUMB))
    except:
      self.log("Exception in Rename Column 'episode'")
    self.sqlcon_wl.commit()
    pass

  def cleanTable(self, DataType):
    try:
      if self.sqlcon_wl:
        if DataType==0:
          self.sqlcursor_wl.execute(QUERY_CLEANTABLE_LIVE_SQLITE) #TODO add data
        elif DataType==1:
          self.sqlcursor_wl.execute(QUERY_CLEANTABLE_SERIES_SQLITE) #TODO add data
        elif DataType==2:
          self.sqlcursor_wl.execute(QUERY_CLEANTABLE_VOD_SQLITE) #TODO add data
        else:
          return
        self.sqlcon_wl.commit()
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
    except SystemExit:
        return 1
    except BaseException:
        self.log(u"Error while remove: %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self.close_db(3)
        return 1

  def _drop_table(self):
    self.log("Drop table...")
    try:
      if self.sqlcon_wl:
        self.sqlcursor_wl.execute(QUERY_DROPTABLE_SQLITE) #TODO add data
        self.sqlcon_wl.commit()
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
    except SystemExit:
        return 1
    except BaseException:
        self.log(u"Error while remove: %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self.close_db(3)
        return 1
    pass

  def remove_item(self, stream):
    self.log("remove item: "+stream)
    try:
      if self.sqlcon_wl:
        self.sqlcursor_wl.execute(QUERY_REMOVE_SQLITE.format(stream)) #TODO add data
        self.sqlcon_wl.commit()
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
    except SystemExit:
        return 1
    except BaseException:
        self.log(u"Error while remove: %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self.close_db(3)
        return 1
    pass

  def list_items(self):
    if self.sqlcon_wl:
      rows=self._doExecute(QUERY_LIST_SQLITE) # self.sqlcursor_wl.execute(QUERY_LIST_SQLITE) #TODO add data
      return rows

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
      xbmc.log("database xtreamdownload: " + s, xbmc.LOGNOTICE)
    else:
      print("database xtreamdownload: " + s)

  pass
