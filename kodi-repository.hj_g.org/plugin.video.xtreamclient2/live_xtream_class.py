# -*- coding: utf-8 -*-
# live xtream API
# Module: live_xtream
# Author: HJ_G.
# Created on: 09.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

#for utf-8 and python3 compatibility
from __future__ import unicode_literals
from __future__ import print_function
import sys
import re

#for testing we have no xbmc
try:
  import xbmc
  print ("No Testing, running with xbmc")
  #from xtutils import start_connection, get_settings, get_url
  from xtutils import *
except Exception as e:
  print ("Testing environent, running without xbmc")
  from xtutils_test import start_connection, get_settings

from client import Client
from categories_class import Categories

"""
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
"""

class Live_Streams:
    def __init__(self):
        self.logging=False
        self.categories_list=None
        self.streams=None
        self.myconfig=None #get_settings()
        self.myclient=None #self._start_connection()

        self._getconfig()
        self._start_connection()
        pass
    def _getconfig(self):
        if self.myconfig==None:
          self.myconfig=get_settings()
        return self.myconfig

    def _start_connection(self):
        if self.myclient==None:
            self.myclient=start_connection()
        myconfig=self._getconfig()
        url = myconfig["url"] + ":" + myconfig["port"] + "?username=" + myconfig["username"] + "&password=" + myconfig["password"]
        if self.myclient==None:
            self.myclient=Client(url)
        return self.myclient

    def get_categories(self, myfilter, myregex):
        """ return a list of categories in a dict[{'category_name','category_id'}, ...]
            
            Parameters:
            myfilter: str = a filter string
            myregex: 'true' or 'false' to use regex for filter string
            if filter is None, settings will be used

            Returns:
            [{'category_name', 'category_id'}, ...]
        """
        if myfilter==None:
          myconfig=self._getconfig()
          myfilter=myconfig['filter']
          myregex=myconfig['filter_is_regex']
        data=self.myclient.live_categories()
        try:
            if myregex=='true':
                p=re.compile(myfilter);
            else:
                p=None
        except Exception:
            self._log("ERROR with regex: "+myfilter)
        if p==None:
            myregex='false'    
        self._log ("myfilter = "+myfilter + ", regex=" +myregex)
        mylist=[]
        if isinstance (data, list):        
            for o in data :
                item={}
                if len(myfilter)>0:
                    if myregex=="true":                        
                        if re.match(p, o['category_name']):                           
                            item['category_name']= o['category_name']
                            item['category_id']=o['category_id']
                            
                        pass
                    else:
                        if o['category_name'].startswith(myfilter):                
                            item['category_name']= o['category_name']
                            item['category_id']=o['category_id']
                else:
                            item['category_name']= o['category_name']
                            item['category_id']=o['category_id']
                if item :
                    mylist.append(item)
                    #cats.add(o['category_name'], o['category_id'])                    
        if isinstance (data, dict):
            print ('ERROR, not a list')

        self.categories_list=mylist
        return self.categories_list

    def _get_category_id(self, category_name):
        if self.categories_list!=None:
          for c in self.categories_list:
            if c['category_name']==category_name:
              return c['category_id']
        return None
    def _get_category_name_by_id(self, category_id):
        if self.categories_list!=None:
            for c in self.categories_list:
                if c['category_id']==category_id:
                  return c
        return None
        pass
    def get_streams_by_category(self, category_id):
        '''this will be used to fill the video list filtered by the category
           
           Returns a list with
           [{'name', 'video', 'thumb', 'category', 'category_id', 'epg_channel_id']
        '''
        myclient=self.myclient # start_connection()#TODO
        category=self._get_category_name_by_id(category_id)
        if category==None:
            category="unknown"
            self._log('ERROR: category_id not found. Did you call get_categories() before?')
        videos=myclient.live_streams_by_category(category_id)    
        if videos==None:
            error=myclient.get_last_error()
            show_dialog("ERROR (3): "+error)
        mylist=[]
        if isinstance (videos, list):        
            for o in videos :
                # Mapping for xbmc list
                if o['epg_channel_id']!=None:
                    """
                    {u'direct_source': u'http://admin-serotv.com:8080/play/v9OQ5ITy76wmBMEitt8VHiCyQUT5BLaKcmIAIf0V7CQXrdRjRhe2WvEcgGS3Iwrf/m3u8', 
                    u'added': u'1622826342', 
                    u'num': 2, 
                    u'name': u'Das Erste HD\u02b0\u1d49\u1d5b\u1d9c', 
                    u'epg_channel_id': u'DASERST', 
                    u'tv_archive': 1, 
                    u'stream_type': u'live', 
                    u'category_ids': [83], 
                    u'stream_id': 57221, 
                    u'custom_sid': u'', 
                    u'stream_icon': u'http://admin-serotv.com:8080/images/51e7682a87cfb0a577b3eb7123710739.png', 
                    u'category_id': u'83', 
                    u'thumbnail': u'', 
                    u'tv_archive_duration': 3}
                    """
                    item={}
                    item['name']=o['name']
                    item['video']=o['direct_source']
                    item['thumb']=o['stream_icon']
                    item['category']=category
                    item['category_id']=o['category_id']
                    item['epg_channel_id']=o['epg_channel_id']
                    # added with version 3.3.0
                    item['tv_archive']=o['tv_archive']
                    item['tv_archive_duration']=o['tv_archive_duration']
                    item['stream_id']=o['stream_id']
                    """if item['tv_archive']==1 and item['tv_archive_duration']>0:
                      print(item)
                    """
                    mylist.append(item)
                    
        if isinstance (videos, dict):
            self._log('videos is a dict! '+ __file__)
            item={}
            item['name']=o['name']
            item['video']=o['direct_source']
            item['thumb']=o['stream_icon']
            mylist.append(item)
            mylist[o['name']]=item #TODO: Why not mylist.append?

        return mylist
        pass

#    def _log(msg, level=xbmc.LOGINFO):
    def _log(self, msg):
        if not self.logging:
            return
        plugin = "plugin.video.xtreamclient"
#        xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
        print("[%s] %s" % (plugin, msg))

    pass #class

