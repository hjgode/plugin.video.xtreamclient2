# -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
#         service.py
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function

import os
import sys
import xbmc
#DEBUG
#xbmc=None

import sqlite3

QUERY_CREATE_MV_SQLITE = "CREATE TABLE IF NOT EXISTS downloadqueue (title TEXT, stream TEXT UNIQUE)"
QUERY_MV_INSERT_SQLITE = 'INSERT OR REPLACE INTO downloadqueue (title, stream) VALUES (?, ?)'
#QUERY_MV_UPDATE_SQLITE = 'UPDATE downloadqueue SET playCount = ?, lastplayed = ?, lastChange = ? WHERE idMovieImdb LIKE ?'
QUERY_REMOVE_MV_SQLITE = "DELETE FROM downloadqueue WHERE stream = '{}';"
QUERY_LIST_SQLITE = "SELECT * from downloadqueue ;"
QUERY_CLEAR_SQLITE = "DELETE FROM downloadqueue;"
QUERY_DROPTABLE_SQLITE = "DROP TABLE downloadqueue;"

class Database:
  def __init__(self, addon_path):
    self.log("Database __init__ ...")
    self.dbpath=addon_path
    self.db_file=os.path.join(self.dbpath + "downloadqueue.sqlite")
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
        self.log(u"Error while opening %s: %s" % (self.dbpath, sys.exc_info()[2]), xbmc.LOGERROR)
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

  def add_item(self, title, stream):
    self.log("add item: " + title + "\n" +stream)

    try:
      if self.sqlcon_wl:
        item=(title, stream)
        self.sqlcursor_wl.execute(QUERY_MV_INSERT_SQLITE,item) #TODO: add data
        self.sqlcon_wl.commit()
        return self.sqlcursor_wl.lastrowid
    except sqlite3.Error as err:
      try:
          errstring = err.args[0]  # TODO: Find out, why this does not work some times
      except BaseException:
          errstring = ''
      self.log('sqlite3 exception: ' + errstring)
    except SystemExit:
        return -1
    except BaseException:
        self.log(u"Error while opening %s: %s" % (self.dbpath, sys.exc_info()[2]))
        self._close_db()
        return -1

    pass

  def _create_table(self):
    self.log("create table...")

    self.sqlcursor_wl.execute(QUERY_CREATE_MV_SQLITE)
    self.sqlcon_wl.commit()
    pass

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
        self.sqlcursor_wl.execute(QUERY_REMOVE_MV_SQLITE.format(stream)) #TODO add data
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
    try:
      if self.sqlcon_wl:
        rows=self.sqlcursor_wl.execute(QUERY_LIST_SQLITE) #TODO add data
        if rows:
          for row in rows:
            self.log(str(row))
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

  def _close_db(self):
    if self.sqlcon_wl:
      self.sqlcon_wl.commit()
      self.sqlcon_wl.close()
      self.sqlcon_wl = 0
      self.log("db closed")

  def log(self, s):
    if xbmc!=None:
      xbmc.log("service xtreamdownload: " + s, xbmc.LOGNOTICE)
    else:
      print("service xtreamdownload: " + s)

  pass
