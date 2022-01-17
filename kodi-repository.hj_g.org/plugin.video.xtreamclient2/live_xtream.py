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
if sys.version_info[0]==2:
  reload(sys)
  sys.setdefaultencoding('utf8')

import re

#from xtutils import start_connection, get_settings, get_url
from xtutils import *

from client import Client

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)

def log(msg, level=xbmc.LOGINFO):
    plugin = "plugin.video.xtreamclient"
    xbmc.log("[%s] %s" % (plugin, msg.encode('utf8')), level)
    
log(CWD)

log(str(sys.version_info))

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

import live_xtream_class

#global
live_streams=None

def get_live_streams_instance():
  global live_streams
  if live_streams==None:
    live_streams=live_xtream_class.Live_Streams()
  return live_streams

def list_live_categories():
  """
  Create the list of video categories in the Kodi interface.
  """
  
  live_streams=get_live_streams_instance() # live_xtream_class.Live_Streams()
  mylist=live_streams.get_categories(None, "")
  # Set plugin category. It is displayed in some skins as the name
  # of the current section.
  xbmcplugin.setPluginCategory(_HANDLE, 'Livestreams Collection')
  # Set plugin content. It allows Kodi to select appropriate views
  # for this type of content.
  xbmcplugin.setContent(_HANDLE, 'videos')
  # Iterate through categories
  for category in mylist: # ['category_name', 'category_id']
    name=category['category_name']
    id=category['category_id']
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=name)
    list_item.setInfo('video', {'title': name,
                                'set': name,
                                'mediatype': 'video'})
    uCategory=name #.encode('utf-8')
    log(u'###uCategory='+uCategory)

    url = get_url(action='listing', category_id=id, category=uCategory)
    
    log(u'###url='+url)
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_HANDLE)

  pass

def list_live_streams(category, category_id):
  """
  Create the list of playable videos in the Kodi interface.

  :param category: Category name
  :type category: str
  """
  xbmcplugin.setPluginCategory(_HANDLE, category)
  xbmcplugin.setContent(_HANDLE, 'videos')
  # Get the list of videos in the category.
  log('###list_live_streams: before get_id() '+ category)
  live_streams=get_live_streams_instance()
  id=category_id
#  id=get_streams_by_category(category)
  videos=live_streams.get_streams_by_category(id)
#  videos = get_videos(id) # get_videos(category)
  # Iterate through videos.
  for video in videos:
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=video['name'])
    # Set additional info for the list item.
    # 'mediatype' is needed for skin to display info for this ListItem correctly.
    id=video['category_id']
    name=video['name']
    genre=video['name']
    name=name.encode('utf-8')
    list_item.setInfo('video', {'title': name,
                                'set': genre, #video['category'],
                                'mediatype': 'video'})

    list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
    # Set 'IsPlayable' property to 'true'.
    # This is mandatory for playable items!
    list_item.setProperty('IsPlayable', 'true')
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
    url = get_url(action='play', video=video['video'])
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

