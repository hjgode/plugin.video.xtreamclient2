# -*- coding: utf-8 -*-
# series xtream API
# Module: series_xtream
# Author: HJ_G.
# Created on: 09.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from __future__ import unicode_literals
from __future__ import print_function

from live_xtream import get_live_streams_instance
"""
Xtream series is organized as:
     Series Categories (ie DE ACTION)
      + Series Infos (ie Game of Thrones)
        + Season 1
          + Episode 1
          + Episode 2
          + ...
        + Season 2
        ...
      + another series info
        + Season x

first get the categories
then list the series (see series_info)
then list the seasons (see series_info) with streams attached
Warning: seasons info is sometimes a list and not a dict!
"""
"""
    url routing
    -----------
    list series categories:
    action=                     params=                     function
    list                        series                      list_series_categories()

    list series in selected category:
    list_series_by_category     category_name
                                category_id                 list_series_by_category

    list seasons in selected series:
    list_seasons_in_series     category_name
                                category_id                 list_seasons_in_series

    list episodes in selected season:
    list_episodes_in_serie      series_id
                                season_number

    play video
"""

import sys
import os
if sys.version_info[0]==2:
  reload(sys)
  sys.setdefaultencoding('utf8')

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
#import xtreamcode_config as cfg


if sys.version_info >= (3,):
    # Python 3: 
    from urllib.parse import urlencode, parse_qsl, quote
else:
    from urllib import quote, urlencode
    from urlparse import urlparse
    import urllib

#my libs
from client import Client
from connection import Connection
from series_stream_class import Series_Streams


# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)

def log(msg, level=xbmc.LOGINFO):
    try:
      level=xbmc.LOGNOTICE
    except:
      level=xbmc.LOGINFO
    plugin = "plugin.video.xtreamclient"
    xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
    print(msg)

log(CWD)

log(sys.version_info)
# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
#_HANDLE = int(sys.argv[1])
from main import _HANDLE

myconfig={} # cfg.config
def get_settings():
    log("get_settings...")
    global myconfig
    myconfig={}
    my_addon = xbmcaddon.Addon()
    #     url = cfg.config["url"] + ":" + cfg.config["port"] + "?username=" + cfg.config["username"] + "&password=" + cfg.config["password"]
    myconfig['url']=my_addon.getSetting('sett_website')
    myconfig['username']=my_addon.getSetting('sett_username')
    myconfig['password']=my_addon.getSetting('sett_password')
    myconfig['port']=my_addon.getSetting('sett_portnumber')
    myconfig['filter']=my_addon.getSetting('sett_filter')
    myconfig['filter_is_regex']=my_addon.getSetting('sett_filter_is_regex') # returns the string 'true' or 'false'
    my_addon.setSetting('my_setting', 'false')
    return myconfig

#class usage
series_streams=None
def get_series_streams_instance():
  global series_streams
  if series_streams==None:
    series_streams = Series_Streams()
  return series_streams

#TODO: Why not use xtutils?
from xtutils import get_url
def get_url2(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    url='{}?{}'.format(_URL, urlencode(kwargs))
    log("get_url: urlencode()="+url)
    return url

############# XBMC lists
"""     action=                     params=
        list                        series
"""

def list_series_categories():
    global _HANDLE
    log("### list_series_category()...")
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, 'Series Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get video categories
    series_streams=get_series_streams_instance()
    myconfig=get_settings()
    myfilter=myconfig['filter']
    myregex=myconfig['filter_is_regex']
    categories = series_streams.get_categories(myfilter, myregex)

    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category['category_name'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        
        #TODO: fixme
        #list_item.setArt({'thumb': VIDEOS.get_categories()[category][0]['thumb'],
        #                  'icon': VIDEOS.get_categories()[category][0]['stream_icon'],
        #                  'fanart': VIDEOS.get_categories()[category][0]['thumb']})
        
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category['category_name'],
                                    'set': category['category_id'],
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='list_series_in_category', category_name=category['category_name'], category_id=category['category_id'])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)

def list_series_in_category(category_name, category_id):
    global _HANDLE
    log("### list_series_in_category")
    xbmcplugin.setPluginCategory(_HANDLE, category_name)
    xbmcplugin.setContent(_HANDLE, 'tvshows')
    
    series_streams=get_series_streams_instance()
    series=series_streams.get_Series_by_category(category_id)

    #myclient=start_connection()
    #series = get_Series_by_category_list(myclient, category_name, category_id) # get_videos(category)
    """
    list[] with dicts print(series_for_category[0].keys())
    dict_keys(['name', 'series_id', 'thumb', 'category_name', 'category_id', 'plot'])
    """
    # Iterate through the series.
    #TODO: add total episodes count? But that would require to get every series info for the listed series
    for serie in series:
        serie_id=serie['series_id']
        serie_name=serie['name']
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=serie_name)
        list_item.setInfo('video', {'title': serie_name,
                                    'set': serie_id,
                                    'mediatype': 'video',
                                    'plot' : serie['plot'],
                                    })
        list_item.setArt({'thumb': serie['thumb'], 'icon': serie['thumb'], 'fanart': serie['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'false')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='list_seasons_in_serie', serie_id=serie_id, serie_name=serie_name, category_name=category_name)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)
    pass

def list_seasons_in_serie(category_name, serie_name, serie_id):
    global _HANDLE
    series_streams=get_series_streams_instance()
    #myinfo=series_streams.get_Series_Info_by_id(series_id)
    data=series_streams.get_myinfo(serie_id)
    
    log("### list_season_in_serie")
#    myclient=start_connection()
#    data=get_series_info(serie_id) # myclient.series_info_by_id(series_id)
    serie_info=data['info'] # a dict
    seasons= data['seasons'] # a list
    #print (seasons)
    episodes=data['episodes'] # a dict
    season_name=serie_name 
    # not all season in seasons is provided, so check if season is in episodes.keys
    xbmcplugin.setPluginCategory(_HANDLE, serie_name+":"+category_name)
    xbmcplugin.setContent(_HANDLE, 'videos')
    """  
    infos: dict_keys(['name', 'title', 'year', 'cover', 'plot', 'cast', 'director', 'genre', 
     'release_date', 'releaseDate', 'last_modified', 'rating', 'rating_5based', 'backdrop_path', 
     'youtube_trailer', 'episode_run_time', 'category_id', 'category_ids'])
     season 1: dict_keys(['air_date', 'episode_count', 'id', 'name', 'overview', 'season_number', 
     'cover', 'cover_big'])
    """
    # Iterate through seasons.
    for season in seasons: # season is a dict
        episode_count=season['episode_count']
        season_number=season['season_number']
        season_name=season['name']
        #episodes may be a dict or a list!
        if isinstance(episodes, dict):
          if not str(season_number) in episodes.keys():
            log("Season "+str(season_number)+" is not available")
            continue
        elif isinstance(episodes, list):
          log ('episodes is list!')
        else:
          log ('episodes type not a dict nor a list!')
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=season_name)
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        # TODO: add number of episodes to season info?
        print(str(season_number)+":"+season_name+" ("+str(episode_count)+")")
        log(str(season_number)+":"+season_name+" ("+str(episode_count)+")")
        #'video' ?
        list_item.setInfo('video', {'title': season_name+" ("+str(episode_count)+")",
                                    'season' : season_number,
                                    'episodeguide' : str(season_number)+" ("+str(episode_count)+")",
                                    'set': season['id'],
                                    'mediatype': 'season',
                                    'plot' : season['overview'],
                                    'genre' : serie_info['genre'],
                                    })
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': season['cover'], 'icon': season['cover'], 'fanart': season['cover_big']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'false')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='list_episodes_in_season', season_number=season_number, serie_name=serie_name, serie_id=serie_id)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)

    pass

def list_episodes_in_season(dummy, season_number, serie_name, serie_id):
    log("### list_episodes_in_season")
    series_streams=get_series_streams_instance()
    xbmcplugin.setPluginCategory(_HANDLE, serie_name+"/"+season_number)
    xbmcplugin.setContent(_HANDLE, 'episodes')

#    data=series_streams.get_myinfo(serie_id) # get_myinfo(serie_id) # myclient.series_info_by_id(series_id)
#    serie_info=data['info'] # a dict
#    seasons=data['seasons'] # a list
#    episodes=data['episodes'] # gives a list
    episodes=series_streams.get_myinfo_episodes(serie_id)
    """  
    infos: dict_keys(['name', 'title', 'year', 'cover', 'plot', 'cast', 'director', 'genre', 
     'release_date', 'releaseDate', 'last_modified', 'rating', 'rating_5based', 'backdrop_path', 
     'youtube_trailer', 'episode_run_time', 'category_id', 'category_ids'])
     season 1: dict_keys(['air_date', 'episode_count', 'id', 'name', 'overview', 'season_number', 
     'cover', 'cover_big'])
    """
    log('season_number: '+str(season_number))
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
      log('season_number not in episodes')
      list_item = xbmcgui.ListItem(label=serie_name)
      list_item.setInfo('video', {'title': "N/A"})
      list_item.setProperty('IsPlayable', 'false')
      is_folder = False
#      url = get_url(action='list_seasons_in_serie', category_name, serie_name, serie_id)
      # Add our item to the Kodi virtual folder listing.
#      xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
      # Add a sort method for the virtual folder items (alphabetically, ignore articles)
      xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
      # Finish creating a virtual folder.
      xbmcplugin.endOfDirectory(_HANDLE)
      return 

    if isinstance(episodes, dict):
      log('episodes is a dict!')  
      if episodes[season_number]==None:
        log('episodes[season_number] is None!')
        return 
    else:
      log('episodes is a list!')
    if isinstance(episodes,dict):
      for video in episodes[season_number]:
        log('looking for video in episodes[season_number]...')
        myplot=""
        try:
          myplot=video['info']['plot']
        except Exception:
          log("ERROR: Missing plot for video")
          log("video dict: "+str(video['info']))
          myplot=""
        
        extension=video['container_extension']
        direct_source=video['direct_source'] #+"."+extension
        log('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
        #print('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
        episode_num=video['episode_num']        
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=serie_name)
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        print('title: '+ video['title'],
                                      ' set: ' + str(season_number),
                                      ' mediatype: '+ 'video',
                                      ' plot: ' + myplot,
                                      ' video: ' + direct_source)
        list_item.setInfo('video', {'title': video['title'],
                                    'set': str(season_number),
                                    'mediatype': 'video',
                                    'plot' : myplot,
                                    'video' : direct_source,
                                    })
        #add a context menu item for download
        cm=[]
        vname=str(video['title'])
        name_url=quote(vname)
        #or
        #name_url=quote(video['title'].encode('utf8'))

        stream_url=quote(direct_source)
        command="RunScript(script.xtreamdownload,?name=%s&stream=%s)" % (name_url, stream_url)
        cm.append( ("Start Download", command) )
        list_item.addContextMenuItems(cm)

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['info']['movie_image'], 'icon': video['info']['movie_image'], 'fanart': video['info']['cover_big']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=direct_source)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    elif isinstance(episodes,list):
      for video in episodes[int(season_number)]:
        #video is another list
        log('video is '+str(type(video)))
        log('looking for video in episodes[season_number]...')
        myplot=""
        try:
          myplot=video['info']['plot']
        except Exception:
          log("ERROR: Missing plot for video")
          myplot=""
        videoinfo=video['info']
        extension=video['container_extension']
        direct_source=video['direct_source'] #+"."+extension
        log('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
        #print('**** list_episodes_in_season(), direct_source=' + video['direct_source'])
        episode_num=video['episode_num']        
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=serie_name)
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        print('title: '+ video['title'],
                                    ' set: ' + str(season_number),
                                    ' mediatype: '+ 'video',
                                    ' plot: ' + myplot,
                                    ' video: ' + direct_source)
        list_item.setInfo('video', {'title': video['title'],
                                    'set': str(season_number),
                                    'mediatype': 'video',
                                    'plot' : myplot,
                                    'video' : direct_source,
                                    })

        #add a context menu item for download
        #test if addon is installed
        if xbmc.getCondVisibility('System.HasAddon(%s)' % "script.xtreamdownload") == 1:
          cm=[]
          if sys.version_info[0]==2:
            name_url=quote(video['title'].encode('utf8'))
          else:
            name_url=quote(video['title'])
          stream_url=quote(direct_source)
          command="RunScript(script.xtreamdownload,?name=%s&stream=%s)" % (name_url, stream_url)
          cm.append( ("Start Download", command) )
          list_item.addContextMenuItems(cm)

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': videoinfo['movie_image'], 'icon': videoinfo['movie_image'], 'fanart': videoinfo['cover_big']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=direct_source)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)
    pass

