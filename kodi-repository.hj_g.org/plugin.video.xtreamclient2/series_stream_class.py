# coding=utf-8
# series xtream API
# Module: series_stream_class
# Author: HJ_G.
# Created on: 09.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

#for utf-8 and python3 compatibility
from __future__ import unicode_literals
from __future__ import print_function
import sys
import re
#from xbmcgui import ListItem

#from xtutils import start_connection, get_settings, get_url

try:
  import xbmc
  from xtutils import start_connection, get_settings
except:
  from xtutils_test import start_connection, get_settings

from client import Client

class Series_Streams:
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
        """ get the list of categories filtered by myfilter with/without regex 
            Params:
              myfilter: str = 'DE ' to filter all starting with 'DE '
              myregex: str = 'true'|'false' to define filter is to be used as regex, ie
                    myfilter='^(DE |TR )' and regex='true' to filter all categories starting with
                    either 'DE ' or 'TR '
            Returns:
              list with dict entries
              [ {'category_name', 'category_id'}, ... 
                            
        """
        if self.myclient==None:
            self.myclient=start_connection()
        data=self.myclient.series_categories()
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

    def get_myinfo(self, series_id):
        self._log("### get_myinfo(series_id)...")
        myinfo=None
        if myinfo==None:
            if self.myclient==None:
              self.myclient=self._start_connection()
            self._log('get_myinfo(series_id)>myinfo=...')
            myinfo = self.myclient.series_info_by_id(series_id)
            if myinfo==None:
              self._log('get_myinfo(series_id)>myinfo==None!')
            else:
              self._log('get_myinfo(series_id)>myinfo OK')
        return myinfo

    def get_myinfo_episodes(self, series_id):
        self._log("### get_myinfo(series_id)...")
        myinfo=None
        if myinfo==None:
            if self.myclient==None:
              self.myclient=self._start_connection()
            self._log('get_myinfo(series_id)>myinfo=...')
            myinfo = self.myclient.series_info_by_id(series_id)
            if myinfo==None:
              self._log('get_myinfo(series_id)>myinfo==None!')
            else:
              self._log('get_myinfo(series_id)>myinfo OK')
        return myinfo['episodes']

    def get_myinfo_serie_info(self, series_id):
        self._log("### get_myinfo(series_id)...")
        myinfo=None
        if myinfo==None:
            if self.myclient==None:
              self.myclient=self._start_connection()
            self._log('get_myinfo(series_id)>myinfo=...')
            myinfo = self.myclient.series_info_by_id(series_id)
            if myinfo==None:
              self._log('get_myinfo(series_id)>myinfo==None!')
            else:
              self._log('get_myinfo(series_id)>myinfo OK')
        return myinfo['info']

    def get_myinfo_seasons(self, series_id):
        self._log("### get_myinfo(series_id)...")
        myinfo=None
        if myinfo==None:
            if self.myclient==None:
              self.myclient=self._start_connection()
            self._log('get_myinfo(series_id)>myinfo=...')
            myinfo = self.myclient.series_info_by_id(series_id)
            if myinfo==None:
              self._log('get_myinfo(series_id)>myinfo==None!')
            else:
              self._log('get_myinfo(series_id)>myinfo OK')
        return myinfo['seasons']

    def list_seasons_in_serie(self, serie_id):
        """ return a list of serie info 
            Params:
              serie_id:str = serie to look for
            Returns:
              list with dicts:
              dict_keys(['air_date', 'episode_count', 'id', 'name', 'overview', 'season_number', 'cover', 'cover_big'])
            """
        self._log("### list_season_in_serie")
        self.myclient=self._start_connection()
        data=self.get_myinfo(serie_id) # myclient.series_info_by_id(series_id)
        if data==None:
          self._log("ERROR: No data for serie_id=" + serie_id)
          return []
        serie_info=data['info'] # a dict serie_info['name']
        seasons=data['seasons'] # a list
        episodes=data['episodes'] # a dict
        season_name=serie_info['name'] 
        # not all season in seasons is provided, so check if season is in episodes.keys
    #    xbmcplugin.setPluginCategory(_HANDLE, serie_name+":"+category_name)
    #    xbmcplugin.setContent(_HANDLE, 'videos')
        """  
        infos: dict_keys(['name', 'title', 'year', 'cover', 'plot', 'cast', 'director', 'genre', 
        'release_date', 'releaseDate', 'last_modified', 'rating', 'rating_5based', 'backdrop_path', 
        'youtube_trailer', 'episode_run_time', 'category_id', 'category_ids'])
        season 1: dict_keys(['air_date', 'episode_count', 'id', 'name', 'overview', 'season_number', 
        'cover', 'cover_big'])
        """
        mylist=[]
        # Iterate through seasons.
        if isinstance(seasons, dict):
          for season in seasons: # season is a dict
              episode_count=season['episode_count']
              season_number=season['season_number']
              season_name=season['name']+' ' +serie_info['name']
              if isinstance(episodes, dict):
                if not str(season_number) in episodes.keys():
                  self._log("Season "+str(season_number)+" is not available")
                  continue
              else:
                self._log("EPISODES is a list!")
              print(str(season_number)+":"+season_name+" ("+str(episode_count)+")")
            # Create a list item with a text label and a thumbnail image.
      #        list_item = xbmcgui.ListItem(label=season_name)
              # Set additional info for the list item.
              # 'mediatype' is needed for skin to display info for this ListItem correctly.
              item={}
              item['title']=season_name
              item['season']=str(season_number)
              item['set']=str(season['id'])
              item['mediatype']='video'
              overview=season['overview']
              if len(overview)>0:
                item['plot']=season['overview']
              else:
                if serie_info['plot']!=None:
                  if len(serie_info['plot'])>0:
                    item['plot']=serie_info['plot']
                  else:
                    item['plot']="no info"
              item['genre']=serie_info['genre']
              mylist.append(item)
        elif isinstance(seasons,list):
          self._log("Seasons is LIST!")
          for season in seasons: # season is a dict
              episode_count=season['episode_count']
              season_number=season['season_number']
              season_name=season['name']+' ' +serie_info['name']
              if isinstance(episodes, dict):
                if not str(season_number) in episodes.keys():
                  self._log("Season "+str(season_number)+" is not available")
                  continue
              else:
                self._log("EPISODES is a list!")
              print(str(season_number)+":"+season_name+" ("+str(episode_count)+")")
            # Create a list item with a text label and a thumbnail image.
      #        list_item = xbmcgui.ListItem(label=season_name)
              # Set additional info for the list item.
              # 'mediatype' is needed for skin to display info for this ListItem correctly.
              item={}
              item['title']=season_name
              item['season']=str(season_number)
              item['set']=str(season['id'])
              item['mediatype']='video'
              overview=season['overview']
              if len(overview)>0:
                item['plot']=season['overview']
              else:
                if serie_info['plot']!=None:
                  if len(serie_info['plot'])>0:
                    item['plot']=serie_info['plot']
                  else:
                    item['plot']="no info"
              item['genre']=serie_info['genre']
              mylist.append(item)
          pass  
        return mylist

    def get_Series_Info_by_id(self, series_id):
      """ get all the seasons and episodes in one call
          Params:
            series_id : str = id of the serie to look for info
          Returns:
            a season list with dict
              [ {'name', 'season', 'season_number', 'stream_id'], 'id'}, ...]
  

      """
      if self.myclient==None:
        self.myclient=self._start_connection()
      data=self.myclient.series_info_by_id(series_id)    
      seasons=data['seasons'] # we also have episodes and info
      mylist=[]
      if isinstance (seasons, list):        
        for o in seasons :
              #TODO: fixme Mapping
              if o['name']!=None:
                  item={}
                  item['name']=o['name'] #season
                  item['season']=o['season_number'] #season
                  #item['episode']
                  item['stream_id']=o['id'] #used as stream name
                  mylist.append(item)
                
        if isinstance (seasons, dict):
            item={}
            item['name']=o['name'] #season
            item['stream_id']=o['id'] #used as stream name
            mylist.append(item)
            mylist[o['name']]=item

      return mylist

    def get_episodes(self, serie_id):
      data=self.get_myinfo(serie_id) # myclient.series_info_by_id(series_id)
      if data==None:
        self._log("ERROR: no data for serie_id (myinfo)")
        return None
      serie_info=data['info'] # a dict
      seasons=data['seasons'] # a list
      episodes=data['episodes'] # gives a list
      return episodes

    def list_episodes_in_season(self, season_number, serie_id):
      """ list all videos in season with seson_number (ie 0,1,2,...) 
          
          Parameters:
          param season_number: str = number of the season to look for, ie 0,1,2...
          param serie_id:str = serie_id number as known by data

          :return
          list of videos with listItem compatible fields
      """
      self._log("### list_episodes_in_season")
      data=self.get_myinfo(serie_id) # myclient.series_info_by_id(series_id)
      if data==None:
        self._log("ERROR: no data for serie_id (myinfo)")
        return None
      serie_info=data['info'] # a dict
      seasons=data['seasons'] # a list
      episodes=data['episodes'] # gives a list
      serie_name=serie_info['name']
      mylist=[]
      """  
      infos: dict_keys(['name', 'title', 'year', 'cover', 'plot', 'cast', 'director', 'genre', 
      'release_date', 'releaseDate', 'last_modified', 'rating', 'rating_5based', 'backdrop_path', 
      'youtube_trailer', 'episode_run_time', 'category_id', 'category_ids'])
      season 1: dict_keys(['air_date', 'episode_count', 'id', 'name', 'overview', 'season_number', 
      'cover', 'cover_big'])
      """
      self._log('season_number: '+str(season_number))
      noEpisodes=False
      if isinstance(episodes, list):
        try:
          if episodes[int(season_number)]==None:
            noEpisodes=True
        except Exception:
          noEpisodes=True
      elif isinstance(episodes, dict):
        if not str(season_number) in episodes:
          noEpisodes=True

      if noEpisodes: #not season_number in episodes: # episodes.keys(): ##episodes[season_number]==None: # gives exception KeyError
        self._log('season_number not in episodes')
        list_item={}
        list_item['label']=serie_name
#        list_item = xbmcgui.ListItem(label=serie_name)
        #list_item.setInfo('video', {'title': "N/A"})
        list_item['title']='N/A'
        list_item['isPlayable']='false'
        #list_item.setProperty('IsPlayable', 'false')
        is_folder = False
        mylist.append(list_item)
        return mylist

      if isinstance(episodes, dict):
        self._log('episodes is a dict!')  
        if episodes[season_number]==None:
          self._log('episodes[season_number] is None!')
          return mylist
      else:
        self._log('episodes is a list!')
      if isinstance(episodes,dict):
        for video in episodes[season_number]:
          self._log('looking for video in episodes[season_number]...')
          myplot=""
          try:
            myplot=video['info']['plot']
          except Exception:
            self._log("list_episodes_in_season dict ERROR: Missing plot for video")
            self._log("video dict: "+str(video['info']))
            myplot=""
          
          extension=video['container_extension']
          direct_source=video['direct_source'] #+"."+extension
          self._log('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
          #print('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
          episode_num=video['episode_num']        
          list_item={}
          # Create a list item with a text label and a thumbnail image.
          #list_item = xbmcgui.ListItem(label=serie_name)
          list_item['label']=serie_name
          # Set additional info for the list item.
          # 'mediatype' is needed for skin to display info for this ListItem correctly.
          list_item['title']=video['title']
          list_item['set']=str(season_number)
          list_item['mediatype']='video'
          list_item['plot']=myplot
          list_item['video']=direct_source

          list_item.update({'thumb': video['info']['movie_image'], 'icon': video['info']['movie_image'], 'fanart': video['info']['cover_big']})
          # Set 'IsPlayable' property to 'true'.
          # This is mandatory for playable items!
          #list_item.setProperty('IsPlayable', 'true')
          mylist.append(list_item)
      elif isinstance(episodes,list):
        for video in episodes[int(season_number)]:
          #video is another list
          self._log('video is '+str(type(video)))
          self._log('looking for video in episodes[season_number]...')
          myplot=""
          try:
            myplot=video['info']['plot']
          except Exception:
            self._log("list_episodes_in_season list ERROR: Missing plot for video")
            myplot=""
          videoinfo=video['info']
          extension=video['container_extension']
          direct_source=video['direct_source'] #+"."+extension
          self._log('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
          #print('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
          episode_num=video['episode_num']        
          # Create a list item with a text label and a thumbnail image.
          list_item={}
          # Create a list item with a text label and a thumbnail image.
          #list_item = xbmcgui.ListItem(label=serie_name)
          list_item['label']=serie_name
          # Set additional info for the list item.
          # 'mediatype' is needed for skin to display info for this ListItem correctly.
          list_item['title']=video['title']
          list_item['set']=str(season_number)
          list_item['mediatype']='video'
          list_item['plot']=myplot
          list_item['video']=direct_source

          list_item.update({'thumb': video['info']['movie_image'], 'icon': video['info']['movie_image'], 'fanart': video['info']['cover_big']})
          # 'mediatype' is needed for skin to display info for this ListItem correctly.
          #print('title: '+ video['title'],
          #                            ' set: ' + str(season_number),
          #                            ' mediatype: '+ 'video',
          #                            ' plot: ' + myplot,
           #                           ' video: ' + direct_source)
          mylist.append(list_item)
      return mylist
    pass

    def get_Series_by_category(self, category):
        """get a list of series for a category_id

          Parameters
          ----------
            myclient: Client: 
              the connected Xtream Client to use
            category_name : str: 
              category name for the series    
            category_id : str: 
              the id to be used to get the series    

          Returns
          -------
            list[] with dicts 
            print(series_for_category[0].keys())

            dict_keys(['name', 'series_id', 'thumb', 'category_name', 'category_id', 'plot'])
        """
        if self.myclient==None:
          self.myclient=self._start_connection()
        videos=self.myclient.series_streams_by_category(category)    
        mylist=[]
        if isinstance (videos, list):        
            for o in videos :
                #TODO: fixme Mapping
                if o['name']!=None:
                    item={}
                    item['name']=o['name']
                    item['series_id']=o['series_id']
                    item['thumb']=o['cover']
                    item['category']=category
                    item['category_id']=o['category_id']
                    item['plot']=o['plot']
                    mylist.append(item)
                    
        if isinstance (videos, dict):
            item={}
            item['name']=o['name']
            item['series_id']=o['series_id']
            item['thumb']=o['cover']
            mylist[o['name']]=item

        return mylist

#    def _log(msg, level=xbmc.LOGINFO):
    def _log(self, msg):
        if not self.logging:
          return
        plugin = "plugin.video.xtreamclient2"
#        xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
        print("[%s] %s" % (plugin, msg.__str__()))

    pass #class
