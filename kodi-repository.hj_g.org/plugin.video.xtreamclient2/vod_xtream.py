# -*- coding: utf-8 -*-
# vod xtream API
# Module: vod_xtream
# Author: HJ_G.
# Created on: 09.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

#for utf-8 and python3 compatibility
from __future__ import unicode_literals
from __future__ import print_function
import sys
import re

if sys.version_info[0]==2:
  reload(sys)
  sys.setdefaultencoding('utf8')

if sys.version_info[0] == 2:
    from urllib import quote
else:
    from urllib.parse import urlencode, parse_qsl, quote
    
#from xtutils import start_connection, get_settings, get_url
from xtutils import *

from client import Client

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

#TODO: remove for release
#import web_pdb
#TODO: remove for release
#web_pdb.set_trace()

import re

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

from xtutils import *
from xtutils import start_connection
from categories_class import Categories
from download_class import Downloader

myclient=None

#global
mydownloader=None
def get_downloader_instance():
  global mydownloader
  if mydownloader==None:
    mydownloader=Downloader()
  return mydownloader

#global
from vod_stream_class import Vod_Streams
vod_streams=None
def get_vod_streams_instance():
  global vod_streams
  if vod_streams==None:
    vod_streams=Vod_Streams()
  return vod_streams

### functions
def get_Vod_categories():
    """return a list of category dicts with category_name and category_id

    001:{u'category_id': u'686', u'category_name': u'DE \u2022 4K Filme 2021', u'parent_id': 0}
        u'category_name':u'DE \u2022 3D Filme'
        u'parent_id':0
        len():3
        special variables
        function variables
        u'category_id':u'686'
        u'category_name':u'DE \u2022 4K Filme 2021'
        u'parent_id':0
        len():3
    """
    vod_streams=get_vod_streams_instance()
    # get unfiltered list
    categories=vod_streams.get_categories('', 'false')
    return categories

def get_vod_by_category(category_id):
  """ return a list of videos using Vod_Streams class """
  vod_streams=get_vod_streams_instance()
  print('#### get_vod_by_category: ' +category_id)
  videos=vod_streams.get_streams_by_category(category_id)
  if videos==None:
      show_dialog("ERROR (4): "+ ' none for get_streams_by_category_name()')
  mylist=[]
  if isinstance (videos, list):        
      for o in videos :
          #TODO: fixme Mapping
          item={}
          item['name']=o['name']
          item['video']=o['video']
          item['thumb']=o['thumb']
          item['category']=o['category']
          item['category_id']=o['category_id']
          item['year']=o['year']
          item['plot']=o['plot']
          item['genre']=o['genre']
          item['title']=o['title']
          mylist.append(item)
          #mylist[o['name']]=item
          #categories[o['category_name']]={}
          #categories[o['category_name']]['category_name']=o['category_name']
          #categories[o['category_name']]['category_id']=o['category_id']
          #cats.add(o['category_name'], o['category_id'])
              
  return mylist
  pass

def list_vod_categories():
  global myconfig
  myconfig=get_settings()
  myfilter=myconfig['filter']
  myregex=myconfig['filter_is_regex']
  vod_streams=get_vod_streams_instance()

  xbmcplugin.setPluginCategory(_HANDLE, 'VideoOnDemand Collection')
  xbmcplugin.setContent(_HANDLE, 'videos')
  # Get video categories using class instance
  categories=vod_streams.get_categories(myfilter,myregex)
  #categories = get_Vod_categories()
  # Iterate through categories
  log("###list_vod_categories: "+str(categories))
  vods=Categories() #use Categories_Class
  for category in categories:
    vods.add(category['category_name'], category['category_id'])
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=category['category_name'])
    list_item.setInfo('video', {'title': category['category_name'],
                                'set': category['category_id'],
                                'mediatype': 'video'})
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&category=Animals
    url = get_url(action='list_vod_for_cat', category_id=category['category_id'], category_name=category['category_name'])
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_HANDLE)
  pass

def list_vod_streams(category_id, category_name):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    mydownloader=get_downloader_instance()

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, category_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get the list of videos in the category.
    #FIXME: need another global for VODs
    id=category_id
    #TODO: FIXME, keyError as dict is looked by a non-utf8 string
    videos = get_vod_by_category(id) # get_vod_videos(id) # get_videos(category)
    log("list_vod_streams...")
    # Iterate through videos.
    for video in videos:
        log("list_vod_streams, list_item=video: "+str(video))
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        id=video['category_id']
        genre=''#VOD.get_name(id) #change for VOD
        list_item.setInfo('video', {'title': video['name'],
                                    'set': genre, #video['category'],
                                    'year':video['year'],
                                    'mediatype': 'video',
                                    "plot" : video["plot"]})

        #FIXME: use something like 'plugin://plugin.video.xtreamclient2/?mode=download&url=example.com'

        #unable to get this working
        """
        cm=[]
        base_url=ADDON.getAddonInfo('id')
        name_url=quote(video['name'])
        stream_url=quote(video['video'])
        downactionurl=get_url(action='download', name=video['name'], stream=video['video'])
        command='"RunAddon(%s)"' % downactionurl
        #command='"RunAddon(plugin://%s/?action=download&title=%s&stream=%s"' % (base_url, name_url, stream_url)
        print("addContextMenuItems: " + command)
        cm.append(('Download stream', command)) 
        list_item.addContextMenuItems(cm)
        #list_item.addContextMenuItems([('Download Stream', 'mydownloader.add_download(video["name"], video["video"]')])
        #base_url='plugin://plugin.video.xtreamclient2/'
        #list_item.addContextMenuItems([('Download Stream', 
        #   'RunPlugin(%sdownload/%s' % (base_url, video['video']))])

        "RunScript(script.xtreamdownload,name=%s,stream=%s)" % (video['name'], video['video'])

        """
        #test if addon is installed
        if xbmc.getCondVisibility('System.HasAddon(%s)' % "script.xtreamdownload") == 1:
          cm=[]
          if sys.version_info[0]==2:
            name_url=quote(video['name'].encode('utf8')) #this is a hack, will not work for all symbols
          else:
            name_url=quote(video['name'])
          stream_url=quote(video['video'])
          command="RunScript(script.xtreamdownload,?name=%s&stream=%s)" % (name_url, stream_url)
          cm.append( ("Start Download", command) )
          list_item.addContextMenuItems(cm)

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
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
