# -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
#         database_update.py
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function

import os
import sys
import re
from categories_class import Categories

#from xtutils_test import start_connection
from vod_stream_class import Vod_Streams
from series_stream_class import Series_Streams
from live_xtream_class import Live_Streams

try:
  import xbmc
  print ("No Testing, running with xbmc")
  #from xtutils import start_connection, get_settings, get_url
  from xtutils import *
except Exception as e:
  print ("Testing environent, running without xbmc")
  from xtutils_test import start_connection, get_settings

import database

myclient=None

class Update_DB:
  def __init__(self, workingdir):
    self.logging=True
    self.myclient=start_connection()    
    self.db=database.Database(workingdir)
    mysettings=get_settings()
    self.myfilter=mysettings['filter']
    self.myregex=mysettings['filter_is_regex']
    self.vod_streams=None # 
    self._get_vod_streams_instance()
    self.series_streams=None #
    self._get_vod_streams_instance()
    self.live_streams=None
    self._get_live_streams_instance()
    pass

  def _get_series_streams_instance(self):
    if self.series_streams==None:
      self.series_streams=Series_Streams()
    return self.series_streams

  def _get_vod_streams_instance(self):
    if self.vod_streams==None:
      self.vod_streams=Vod_Streams()
    return self.vod_streams

  def _get_live_streams_instance(self):
    if self.live_streams==None:
      self.live_streams=Live_Streams()
    return self.live_streams

  def updateLive(self, callback):
    iDataType=0
    myfilter=self.myfilter
    myregex=self.myregex
    live_streams=self._get_live_streams_instance()
    categories=live_streams.get_categories(myfilter, myregex)

    vod_count=0
    num_cat=len(categories)
    catcount=0
    total_live=0
    if callback!=None:
      callback("total categories: ", num_cat)
    for c in categories:
      mylist=[] # use smaller lists
      catcount=catcount+1
      category_name=c['category_name']
      category_id=c['category_id']
      videos=live_streams.get_streams_by_category(category_id)
      if callback:
        percent=int(catcount/num_cat*100)  # ie num_cat=30 and catcount=3 => 3/30=0.1=>10%
        callback("processing live cats: "+category_name, percent)
      if isinstance(videos,list):
        num_live=len(videos)
        live_count=0
        for o in videos :
          live_count=live_count+1
          mylist.append((iDataType, o['name'], category_id, category_name, 
          o['video'], "", "", o['thumb']))
          if callback:
            percent=int(live_count/num_live*100)
            callback("processing live: ", percent)
        total_live=total_live+num_live
      if len(mylist) > 0:
        self.db.add_many(mylist)
    return total_live
    pass

  def updateVOD(self, callback=None):
    #DataType is 2
    iDataType=2
    #data=self.myclient.vod_categories()
    myfilter=self.myfilter
    myregex=self.myregex
    vod_streams=self._get_vod_streams_instance()
    categories=self.vod_streams.get_categories(myfilter, myregex)
    
    vod_count=0
    num_cat=len(categories)
    if callback!=None:
      callback("total categories: ", num_cat)
    catcount=0
    total_vod=0
    for c in categories:
      mylist=[] # use smaller lists

      catcount=catcount+1
      category_name=c['category_name']
      category_id=c['category_id']
      videos=vod_streams.get_streams_by_category(category_id)
      if callback:
        percent=int(catcount/num_cat*100)
        callback("processing vod cats: ", percent)
      if isinstance(videos,list):
        num_vod=len(videos)
        vod_count=0
        for o in videos :
          vod_count=vod_count+1
          mylist.append((iDataType, o['name'], category_id, category_name, 
          o['video'], "", "", o['thumb']))
          if callback:
            percent=int(vod_count/num_vod*100)
            callback("processing vod: ", percent)
        total_vod=total_vod+num_vod
      if len(mylist) > 0:
        self.db.add_many(mylist)
    return total_vod
    pass

  def updateSeries(self, callback=None):
    #DataType is 1
    iDataType=1
    #data=self.myclient.vod_categories()
    myfilter=self.myfilter
    myregex=self.myregex
    series_streams=self._get_series_streams_instance()
    categories=self.series_streams.get_categories(myfilter, myregex)
    
    catcount=0
    season_count=0
    series_count=0
    num_cat=len(categories)
    if callback!=None:
      callback("total series categories: ", num_cat)
    total_series=0
    for c in categories:
      catcount=catcount+1
      category_name=c['category_name']
      category_id=c['category_id']
      series=series_streams.get_Series_by_category(category_id)
      if callback!=None:
        percent=int(catcount/num_cat*100)
        callback("processing category: "+category_name, percent)
      mylist=[] # use smaller lists
      num_series=len(series)
      season_count=0
      for s in series:
        """
        {u'category': u'733', u'category_id': u'733', u'name': u'Rebelde - Jung und rebellisch', u'plot': u'In der Elite Way School beginnt das neue Schuljahr. Ein feindlicher Geheimbund droht die musikalischen Ambitionen der neuen Sch\xfcler knallhart platzen zu lassen.', u'series_id': 1836, u'thumb': u'http://admin-serotv.com:8080/images/_SVxa7n9H4Bo0kOFoOeVIiW4FRtD9mRXbmS6zUXwE9-42NvbpmWf-z-RbLpAGZPAthCT2pGVfZWmPnkGLOX9GJT7yJduurPHi4njOH0DWrU.jpg'}
        """
        series_count=series_count+1
        series_id=s['series_id']
        series_name=s['name']
        series_thumb=s['thumb']
        if callback!=None:
          percent=int(series_count / num_series * 100)
          callback("processing series: "+series_name, percent)
        #for series we don not provide a stream!
        #otherwise it would take ages to iterate to all series, their seasons and episodes
        mylist.append((iDataType, series_name, category_id, category_name, 
          "", series_id, "", series_thumb))
        continue
      total_series=total_series+num_series  
      self.db.add_many(mylist)
    
    return total_series

  pass
  
  def cleanTable(self, DataType):
    """ clear table for DataType=[0|1|2] (Live, Series, VOD)"""
    self.db.cleanTable(DataType)

  def find(self, findstr, search_area=None):
    myresult = self.db.find(findstr, typ=search_area)
    return myresult
    pass
  def _log(self, msg):
    if not self.logging:
      return
    plugin = "plugin.video.xtreamclient: database_update class"
    if xbmc!=None:
      xbmc.log(plugin +" " + msg, xbmc.LOGDEBUG)
    else:
      print("[%s] %s" % (plugin, msg))
