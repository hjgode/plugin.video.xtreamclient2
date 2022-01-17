# coding=utf-8
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

class Vod_Streams:
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
        self.myconfig=get_settings()
    def _start_connection(self):
        if self.myclient==None:
            self.myclient=start_connection()
        myconfig=self.myconfig
        url = myconfig["url"] + ":" + myconfig["port"] + "?username=" + myconfig["username"] + "&password=" + myconfig["password"]
        if self.myclient==None:
            self.myclient=Client(url)
        return self.myclient
    def get_categories(self, myfilter, myregex):
        """ return the list of categories as dicts of [{'category_name','category_id'},...] """
        data=self.myclient.vod_categories()
        if data==None:
          error=myclient.get_last_error()
          self._log("ERROR (getting VOD cats): "+error)

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
        if isinstance (data, dict):
            print ('ERROR, not a list')

        self.categories_list=mylist
        return self.categories_list
    def _get_category_name_by_id(self, category_id):
        if self.categories_list!=None:
            for c in self.categories_list:
                if c['category_id']==category_id:
                    return c['category_name']
        return None
        pass
    def _get_category_id_by_name(self, category_name):
      if self.categories_list!=None:
          for c in self.categories_list:
              if c['category_name']==category_name:
                  return c['category_id']
      return None
      pass
    def get_streams_by_category_name(self, category_name):
      category_id=self._get_category_id_by_name(category_name)
      if category_id==None:
        return None
      return self.get_streams_by_category(category_id)
      pass

    def get_streams_by_category(self, category_id):
        '''this will be used to fill the video list filtered by the category
        
          Returns a list of dict with: [ {'name', 'video', 'thumb', 'category', 'category_id', 'year', 'plot', 'genre', 'title'}, ...]
        '''
        myclient=start_connection()
        category=self._get_category_name_by_id(category_id)
        if category==None:
            category="unknown"
            self._log('ERROR: category_id not found. Did you call get_categories() before?')
        videos=myclient.vod_streams_by_category(category_id)    
        if videos==None:
            error=myclient.get_last_error()
            show_dialog("ERROR (3): "+error)
        mylist=[]
        if isinstance (videos, list):        
            for o in videos :
                # Mapping for xbmc list
                item={}
                item['name']=o['name']
                item['video']=o['direct_source']
                item['thumb']=o['stream_icon']
                item['category']=category
                item['category_id']=o['category_id']
                item['year']=o['year']
                item['plot']=o['plot']
                item['genre']=o['genre']
                item['title']=o['title']
                mylist.append(item)
                    
        if isinstance (videos, dict):
                item={}
                item['name']=o['name']
                item['video']=o['direct_source']
                item['thumb']=o['stream_icon']
                item['category']=category
                item['category_id']=o['category_id']
                item['year']=o['year']
                item['thumb']=o['stream_icon']
                item['plot']=o['plot']
                item['genre']=o['genre']
                item['title']=o['title']
                mylist.append(item)

        return mylist
        pass
#    def _log(msg, level=xbmc.LOGINFO):
    def _log(self, msg):
        if not self.logging:
            return
        plugin = "plugin.video.xtreamclient"
#        xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
        print("[%s] %s" % (plugin, msg.__str__()))

    pass #class
