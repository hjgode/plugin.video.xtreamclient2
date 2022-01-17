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
import datetime

from livearchive_database import EPG_Database

try:
  import xbmc
  print ("No Testing, running with xbmc")
  #from xtutils import start_connection, get_settings, get_url
  from xtutils import *
  CWD = xbmcaddon.Addon().getAddonInfo('path')
except Exception as e:
  print ("Testing environent, running without xbmc")
  from xtutils_test import start_connection, get_settings
  CWD=os.path.dirname(__file__)

from simple_epg import Simple_Epg

from live_xtream_class import Live_Streams
from client import Client

class LiveArchive:
  def __init__(self):
    self.live_streams=None
    self._get_live_streams_instance()
    self.myclient=None
    self.simple_epg= Simple_Epg()
    self.mysettings=None
    self.myfilter=None
    self.myregex=None
    self._get_settings()

    self.epg_database=EPG_Database(CWD)
    pass # init

  def _get_settings(self):
    if self.mysettings==None:
      self.myclient=start_connection()
      self.mysettings=get_settings()
      self.myfilter=self.mysettings['filter']
      self.myregex=self.mysettings['filter_is_regex']

  def _get_live_streams_instance(self):
    if self.live_streams==None:
      self.live_streams=Live_Streams()
    return self.live_streams

  def _log(self, msg):
    if xbmc==None:
      print(msg)
    else:
      xbmc.log(msg, xbmc.LOGDEBUG)
    pass

  def get_timshift_url(self, stream_id, start, duration):
    myclient=self.myclient
    # this will start streaming!
    url = myclient.play_timeshift(stream_id, start, duration)
    #self._log("play_timeshift stream is: " + url)
    return url
    pass

  def get_first_last(self):
    """ return the oldest and newest times inside EPG database"""
    (first, last) = self.epg_database.get_first_last();
    return (first, last)
    pass

  def find(self, title):
    """ return epg entries for search string

      Returns:
      list of simple_epg info as tuple
      (stream_id, title, description, start, end, duration)

      [(57229, u'Supergirl', u"Als ein Syvillianer ermordet wird, entdecken Kara und Alex ein illegales Alien-Box-Kartell. Die Betreiberin Veronica Sinclair ist in diesen Kreisen als `Roulette' bekannt. Undercover treffen sie auf M'gann, die f\xfcr Roulette als K\xe4mpferin antritt.", u'2022-01-12 00:00:00', u'2022-01-12 01:00:00', u'60'),...]
    """
    mylist=self.epg_database.find(title)
    return mylist
    pass

  def get_simple_epg(self, channel_stream_id, channel_name, update=False, callback=None):
    """ return simple epg 
        Returns:
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
    channel_info={}
    channel_info['channel_stream_id']=channel_stream_id
    channel_info['channel_name']=channel_name
    epg_infos=[]
    #simple_epg= Simple_Epg()
    if update:
      epgdata = self.simple_epg.get_simple_epg(channel_stream_id)
      num_epg=len(epgdata)
      cnt_epg=0
      for epg in epgdata:
        cnt_epg=cnt_epg+1
        if callback:
          callback("Processing "+channel_name +"... ", int((cnt_epg*100)/num_epg) )
        if epg['has_archive']==1:
          epg_infos.append(epg)
      self.epg_database.add_epg(channel_stream_id, epg_infos)

      pass # if update
    elif not update:
      epgdata=self.epg_database.get_epgLast30(channel_stream_id)
      for epg in epgdata:
        #if epg['has_archive']==1: #not needed as we read the database
        epg_infos.append(epg)
      pass # if not update

    return epg_infos
    pass

  
  #shortcut for xbmc
  def get_categories(self):
    """ return a list of channels that provide an archive
        Uses database 
        Returns:
          channel_name=channel['name']
          channel_stream_id=channel['stream_id']
    """
    return self.get_channels_with_archive(update=False)

  def get_epg(self, channel_stream_id):
    """
      for XBMC listing using database
      returns:
        epg['channel_stream_id']=channel_stream_id
        epg['title']=row[0]
        epg['description']=row[1]
        epg['start']=row[2]
        epg['end']=row[3]
        epg['duration']=row[4]
    """
    
    epg_infos=self.epg_database.get_epg(channel_stream_id)
    return epg_infos
    pass

  def get_channels_with_archive(self, update=False, callback=None):
    """ return a list of channels that provide an archive 
        Returns:
          channel_name        =channel['name']
          channel_stream_id   =channel['stream_id']
          channel_thumb       =channel['thumb']
        [{'channel_name': u'Das Erste HD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57221, 'thumb': u'http://admin-serotv.com:8080/images/51e7682a87cfb0a577b3eb7123710739.png'}, 
         {'channel_name': u'ZDF HD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57218, 'thumb': u'http://admin-serotv.com:8080/images/c122a3a1ce18196b80dd05d6e89d133c.png'}, {'channel_name': u'RTL FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57224, 'thumb': u'http://admin-serotv.com:8080/images/fad43a900e339c2c9875909ca2facfc7.png'}, {'channel_name': u'SAT.1 FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57222, 'thumb': u'http://admin-serotv.com:8080/images/91b12cf39586a2ade6ad736724534660.png'}, {'channel_name': u'ProSieben FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57230, 'thumb': u'http://admin-serotv.com:8080/images/e34aae1a5e1e05239a94368add0dd0b1.png'}, {'channel_name': u'RTLII FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57225, 'thumb': u'http://admin-serotv.com:8080/images/ec4732df98285c11a913a3e86c3c0b72.png'}, {'channel_name': u'VOX FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57227, 'thumb': u'http://admin-serotv.com:8080/images/816494f8dbbf57c042a0141153009b76.png'}, {'channel_name': u'Kabel Eins FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57228, 'thumb': u'http://admin-serotv.com:8080/images/9f9d136866ef8cce926c9d33aebffb57.png'}, {'channel_name': u'SAT.1 Gold FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57223, 'thumb': u'http://admin-serotv.com:8080/images/8afd473cc419a0a4acfd26fe162c6f4a.png'}, {'channel_name': u'Sixx FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57229, 'thumb': u'http://admin-serotv.com:8080/images/20c6694eac1dce900073f90e8759e0f0.png'}, {'channel_name': u'ProSieben MAXX FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57231, 'thumb': u'http://admin-serotv.com:8080/images/ffcacb25243c957d688ce8a6a27b6306.png'}, {'channel_name': u'Nitro FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57232, 'thumb': u'http://admin-serotv.com:8080/images/a4e01fd8b8e20d028094ca70dc11c6e5.png'}, {'channel_name': u'COMEDY CENTRAL FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57233, 'thumb': u'http://admin-serotv.com:8080/images/734686ddfc2dffdcec5f359dddac6f8f.png'}, {'channel_name': u'TELE 5 FHD\u02b0\u1d49\u1d5b\u1d9c', 'channel_stream_id': 57234, 'thumb': u'http://admin-serotv.com:8080/images/5a2a6e65332549518f1a736c3a3e1516.png'}, ...]

    """
    if not update:
      mylist=self.epg_database.get_channels();
      return mylist
    live_streams=self._get_live_streams_instance()
    categories=live_streams.get_categories(self.myfilter, self.myregex)
    mylist=[]
    if update:
      self.epg_database.cleanTableLIVE()
    num_cats=len(categories)
    cnt_cat=0
    for c in categories:
      category_name=c['category_name']
      category_id=c['category_id']
      cnt_cat=cnt_cat+1
      if callback:
        callback("Searching category: "+category_name, (cnt_cat*100) / num_cats)
      streams=live_streams.get_streams_by_category(category_id)
      self._log("searching thru "+category_name)
      if isinstance(streams,list):
        cnt_streams=0
        num_stream_in_cat=len(streams)
        for channel in streams:
          """
          {u'category': 
          {u'category_id': u'83', u'category_name': u'DE \u2022 FullHD\u02b0\u1d49\u1d5b\u1d9c'}, 
          u'category_id': u'83', 
          u'epg_channel_id': u'DASERST', 
          u'name': u'Das Erste HD\u02b0\u1d49\u1d5b\u1d9c', 
          u'stream_id': 57221, 
          u'thumb': u'http://admin-serotv.com:8080/images/51e7682a87cfb0a577b3eb7123710739.png', 
          u'tv_archive': 1, 
          u'tv_archive_duration': 3, 
          u'video': u'http://<server>:<port>/play/v9OQ5ITy76wmBMEitt8VHiCyQUT5BLaKcmIAIf0V7CQXrdRjRhe2WvEcgGS3Iwrf/m3u8'
          }
          """
          cnt_streams=cnt_streams+1
          if callback:
            callback("Searching streams: " + channel['name'], (cnt_streams*100) / num_stream_in_cat)
          if channel['tv_archive']==1:
            #we found a channel with archive
            #mylist.append(channel)
            channel_name=channel['name']
            channel_stream_id=channel['stream_id']
            channel_thumb=channel['thumb']
            mylist.append({'channel_name':channel_name, 'channel_stream_id':channel_stream_id, 'thumb':channel_thumb})
            
            self.epg_database.addChannel(channel_name, channel_stream_id, channel_thumb)

            ##### No need to update EPG here?
            """
            if not update:
              epg_infos=self.epg_database.get_epg(channel_stream_id)
              channel_info['simple_epg']=epg_infos
              mylist.append(channel_info)
            if update:
              self.epg_database.addChannel(channel_name, channel_stream_id, channel_thumb)
              ### Add epg_data
              simple_epg= Simple_Epg()
              epgdata = simple_epg.get_simple_epg(channel_stream_id)
              channel_info={}
              channel_info['channel_stream_id']=channel_stream_id
              channel_info['channel_name']=channel_name
              channel_info['thumb']=channel_thumb
              epg_infos=[]
              num_epg=len(epgdata)
              cnt_epg=0
              for epg in epgdata:
                if epg['has_archive']==1:
                  cnt_epg=cnt_epg+1
                  if callback:
                    callback("Adding EPG for: "+channel_name, int((100*cnt_epg)/num_epg))
                  epg_infos.append(epg)
  #                mylist.append(epg_infos)
              # 'Diese Sendung berichtet \xc3\xbcber die aktuellsten und wichtigsten Nachrichten der Bundesrepublik.'
              # get epg for tv_archive_duration?
              channel_info['simple_epg']=epg_infos
              self.epg_database.add_epg(channel_stream_id, epg_infos)
              mylist.append(channel_info)
              channel_info={}
              epg_infos=[]
            """
    return mylist
    pass

  #TODO: ? get all infos at once (takes some time), or use a service or just
  # get channels with archive first and then epg when requested? 
  
  def _get_archive_streams(self):
    """ DO NOT USE """
    live_streams=self._get_live_streams_instance()
    categories=live_streams.get_categories(self.myfilter, self.myregex)
    mylist=[]
    for c in categories:
      category_name=c['category_name']
      category_id=c['category_id']
      streams=live_streams.get_streams_by_category(category_id)
      self._log("searching thru "+category_name)
      if isinstance(streams,list):
        for channel in streams:
          if channel['tv_archive']==1:
            #we found a channel with archive
            #mylist.append(channel)
            channel_name=channel['name']
            channel_stream_id=channel['stream_id']
            """
            {u'category': 
            {u'category_id': u'83', u'category_name': u'DE \u2022 FullHD\u02b0\u1d49\u1d5b\u1d9c'}, 
            u'category_id': u'83', 
            u'epg_channel_id': u'DASERST', 
            u'name': u'Das Erste HD\u02b0\u1d49\u1d5b\u1d9c', 
            u'stream_id': 57221, 
            u'thumb': u'http://admin-serotv.com:8080/images/51e7682a87cfb0a577b3eb7123710739.png', 
            u'tv_archive': 1, 
            u'tv_archive_duration': 3, 
            u'video': u'http://<server>:<port>/play/v9OQ5ITy76wmBMEitt8VHiCyQUT5BLaKcmIAIf0V7CQXrdRjRhe2WvEcgGS3Iwrf/m3u8'
            }
            """
            #print(channel)
            simple_epg= Simple_Epg()
            epgdata = simple_epg.get_simple_epg(channel_stream_id)
            channel_info={}
            channel_info['channel_stream_id']=channel_stream_id
            channel_info['channel_name']=channel_name
            epg_infos=[]
            for epg in epgdata:
              if epg['has_archive']==1:
                epg_infos.append(epg)
#                mylist.append(epg_infos)
                """
                  Returns:
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

                  {u'lang': u'de', 
                  u'start_timestamp': 1641716101, 
                  u'end': u'2022-01-09 10:15:01', 
                  u'description': 'Die Sendereihe zeigt eine Zusammenfassung aller Spiele und Tore des aktuellen Spieltags.', 
                  u'start': u'2022-01-09 09:15:01', 
                  u'now_playing': 0, 
                  u'title': 'Admiral BL: Alle Spiele, alle Tore', 
                  u'epg_id': u'22', 
                  u'channel_id': u'skysportaustria.at_1', 
                  u'has_archive': 1, 
                  u'id': 1641716100, 
                  u'stop_timestamp': 1641719701}
                """
            # get epg for tv_archive_duration?
            channel_info['simple_epg']=epg_infos
            mylist.append(channel_info)
            channel_info={}
            epg_infos=[]
        #end has_archive
    return mylist
    pass # get archive streams

  def play_archive(self, stream_id, start, duration):
    myconfig=self.mysettings
    url = myconfig["url"] + ":" + myconfig["port"] + "?username=" + myconfig["username"] + "&password=" + myconfig["password"]
    myclient=Client(url)
    path=myclient.play_timeshift(stream_id,start,duration)
    return path

  pass # ret
