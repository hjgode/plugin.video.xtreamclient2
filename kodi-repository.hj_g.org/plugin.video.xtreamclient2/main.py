# -*- coding: utf-8 -*-
#for python2
# Module: main
# version 2.4.5
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video Xtream client plugin that is compatible with Kodi 18?

For debug view in web browser install addon web_pdb in kodi
in code add
#TODO: remove for release
#import web_pdb
#TODO: remove for release, makes script stop, see browser localhost:5555
#web_pdb.set_trace()

TODO: Split code in samller files for Live and VOD
  DONE

#TODO:
  add search dialogs: DONE
  add live_archive
  
"""
import sys
import os
from search_xtream import showSearchOptions

if sys.version_info[0] == 3:
    # Python 3: 
    from urllib.parse import urlencode, parse_qsl
else:
    import urllib
    from urlparse import urlparse
    from urlparse import parse_qsl
    import re
    

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

#TODO: remove for release
#import web_pdb
#TODO: remove for release
#web_pdb.set_trace()


# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)

from xtutils import *

#for development use this
#import xtreamcode_config as cfg

file_path = os.path.realpath(__file__)
print("###running script: " + file_path) 
log("###running script: " + file_path)

from client import Client
from connection import Connection

from series_xtream import *
from vod_xtream import *

from search_xtream import showSearchInput, showSearchOptions, showSearchResults

# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

from categories_class import Categories

from live_xtream import *
from live_archive_xbmc import *


def list_stream_types():
    global CWD
    myconfig=get_settings()
    mysettfilter=myconfig['filter']
    mysettisregex=myconfig['filter_is_regex']
    log('list_stream_types: Filter="'+mysettfilter+'", regex='+mysettisregex)
    xbmcplugin.setPluginCategory(_HANDLE, 'Select stream type:')
    
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get video categories
    TYPES = {'Live Streams': {'name': 'livestreams',
                       'thumb': os.path.join( CWD, 'resources', 'live_icon.jpg' ),
                       'properties':{}},
             'Videos': {'name': 'videos',
                        'thumb': os.path.join( CWD, 'resources', 'vod_icon.jpg' ),
                        'properties':{}},
             'Series': {'name': 'series',
                       'thumb': os.path.join( CWD, 'resources', 'series_icon.jpg' ),
                        'properties':{}},
             'Search Live/Series/VOD': {'name': 'search',
                       'thumb': os.path.join( CWD, 'resources', 'search_icon.jpg' ),
                        'properties':{'SpecialSort':'bottom'}},
             'Live archive': {'name': 'live_archive',
                       'thumb': os.path.join( CWD, 'resources', 'search_icon.jpg' ),
                        'properties':{}},
             'Search Live archive': {'name': 'search_live_archive',
                       'thumb': os.path.join( CWD, 'resources', 'search_icon.jpg' ),
                        'properties':{'SpecialSort':'bottom'}},
                       }
    # Iterate through categories
    for t in TYPES:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=t)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        #TODO: fixme
#        image= os.path.join( CWD, 'resources', 'live_icon.jpg' )
        list_item.setArt({'icon': TYPES[t]['thumb']})
        #list_item.setArt({'thumb': VIDEOS.get_categories()[category][0]['thumb'],
        #                  'icon': VIDEOS.get_categories()[category][0]['stream_icon'],
        #                  'fanart': VIDEOS.get_categories()[category][0]['thumb']})
        
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': t,
                                    'genre': t,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        if TYPES[t]['name']=='search':
          url = get_url(action='searchoptions')
          pass
        elif TYPES[t]['name']=='live_archive':
          url = get_url(action='live_archive')
          pass            
        elif TYPES[t]['name']=='search_live_archive':
          url = get_url(action='search_live_archive')
          pass            
        else:
          url = get_url(action='list', type=TYPES[t]['name'])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        if len(TYPES[t]['properties'])>0:
          list_item.setProperties(TYPES[t]['properties'])
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.

    play_item = xbmcgui.ListItem(path=path)
    
    log("**** play_video: "+path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def router(paramstring):
    global _HANDLE
    print('main router: _HANDLE='+str(_HANDLE))

    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    myconfig=get_settings()
    log("filter: "+myconfig['filter']+", regex: "+myconfig['filter_is_regex'])
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    log("###router called with: " + str(params))
    if params:
        # url = get_url(action='list_vod_for_cat', category=category['category'], category_id=category['category_id'])
        if params['action'] == 'list_vod_for_cat':
#            if params['category']:
#                log("router calling list_vod_for_category...")
            if params['category_id']:
                list_vod_streams(params['category_id'], params['category_name'])
        elif params['action']=='searchoptions':
            showSearchOptions()
            pass
        elif params['action']=='live_archive':
            list_livearchive_channels()
            pass
        elif params['action']=='search_live_archive':
            search_archive()
            pass
        elif params['action']=='live_archive_epg':
            channel_stream_id=params['category_id']
            list_channel_epg_infos(channel_stream_id)
            pass
        elif params['action']=="list_series_in_category":
            if params['category_id'] and params['category_name']:
                log("router: list_series_in_category/"+params['category_id'] + ", " + params['category_name'])
                list_series_in_category(params['category_name'], params['category_id'])

        elif params['action']=="list_seasons_in_serie":
            if params['serie_id'] and params['serie_name'] and params['category_name']:
                log("router: list_seasons_in_serie/"+params['category_name']+ ", "+params['serie_name'] + ", " + params['serie_id'])
                list_seasons_in_serie(params['category_name'], params['serie_name'], params['serie_id'])
                log("router: list_seasons_in_serie DONE")
        elif params['action']=="list_episodes_in_season":
            #list_episodes_in_season(season_number:str, series_name:str, series_id:str):
            log("router() list_episodes_in_season...")
            if params['season_number'] and params['serie_name'] and params['serie_id']:
              list_episodes_in_season(None, params['season_number'], params['serie_name'], params['serie_id'])
            pass

        elif params['action'] == 'list': #list called with type = livestreams,videos or series
            if params['type']=='livestreams':
                log("router calling list_live_categories...")
                list_live_categories()
            elif params['type']=='videos':
                list_vod_categories()
            elif params['type']=='series':
                list_series_categories()

        elif params['action'] == 'listing':
            # Display the list of videos in a provided category.
            #log("###listing for category: "+params['category'])
            log('###listing action, live by category: '+params['category']+', id=' + params['category'])
            #TODO: remove for release
            #web_pdb.set_trace()
            
            list_live_streams( params['category'], params['category_id'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_stream_types() #list_live_categories()


if __name__ == '__main__':
    print ('#### %s args ####' % ADDON.getAddonInfo('id'))
    for a in sys.argv:
      print (a)
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
