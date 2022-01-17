# -*- coding: utf-8 -*-
# live archive xtream API
# Module: live_archive_xbmc
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
    try:
      level=xbmc.LOGNOTICE
    except:
      level=xbmc.LOGINFO
    plugin = "plugin.video.xtreamclient:live_archive_xbmc"
    xbmc.log("[%s] %s" % (plugin, msg.encode('utf8')), level)
    
log(CWD)

log(str(sys.version_info))

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

from live_archive import LiveArchive

#global
live_archive=LiveArchive()
myclient=start_connection()

progress=None
def showProgress(msg, percent, update=False, close=False):
  global progress
  if progress==None:
    progress=xbmcgui.DialogProgress()
    progress.create("Searching...", msg)
  if update:
    progress.update(percent, msg)
  if close:
    progress.close()
  pass

def showProgressUpdate(msg, percent):
  global progress
  showProgress(msg, percent, update=True, close=False)
  pass

def showArchiveSearchInput():
  dlg=xbmcgui.Dialog()
  input=dlg.input("Enter Search term", "", xbmcgui.INPUT_ALPHANUM)
  if len(input)==0:
    return None
  return input
  pass

def search_archive():
  log("Entering Archive search...")
  global live_archive

  #update DB?
  selectionlist=['Channels and Archive EPG', 'EPG only', 'Use existing data']
  dlg=xbmcgui.Dialog()
  selectedoption=dlg.select("Update database", selectionlist)
  if selectedoption==-1:
    return
  if selectedoption==0:
    #update both
    channel_list=live_archive.get_channels_with_archive(update=True, callback=showProgressUpdate)
    for channel in channel_list:
      live_archive.get_simple_epg(channel_stream_id=channel['channel_stream_id'], channel_name=channel['channel_name'], update=True, callback=showProgressUpdate)
    pass
  elif selectedoption==1:
    #update EPG only
    channel_list=live_archive.get_channels_with_archive(update=False, callback=None)
    for channel in channel_list:
      live_archive.get_simple_epg(channel_stream_id=channel['channel_stream_id'], channel_name=channel['channel_name'], update=True, callback=showProgressUpdate)
    pass
  else:
    #use existing data
    pass
  
  findstr=showArchiveSearchInput()
  if findstr==None:
    log('Archive Search canceled!')
    return
  
  mylist=live_archive.find(findstr)
  if mylist==None:
    dlg=xbmcgui.Dialog()
    dlg.ok('Search Archive', 'Nothing found for '+findstr)
    return
  xbmcplugin.setContent(_HANDLE, 'videos')
  for epg in mylist:
    (stream_id, title, description, start, end, duration)=epg
    stream=live_archive.get_timshift_url(stream_id, start, duration)
    list_item=xbmcgui.ListItem(label=title, label2=start)
    list_item.setInfo('video', {'title': start+" " +end+" " + title,
                                'genre': 'live archive',
                                'mediatype': 'video',
                                  'plot': description})    
    list_item.setProperty('IsPlayable', 'true')
    url=stream
    is_folder=False
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_GENRE )
  xbmcplugin.endOfDirectory(_HANDLE)

  pass

def list_livearchive_channels():
  """
  Return the list of channels with archive set for the Kodi interface.
  """
  global live_archive
  dlg=xbmcgui.Dialog()
  (first, last)=live_archive.get_first_last()
  do_update=dlg.yesno("Database update?", "Update archive data? Only the last 30hours will work. "+ "(oldest="+first+", last="+last+")" )
  if do_update==-1:
    return
  elif do_update:
    yesno2=dlg.yesno("Database update", "Update channels with archive first?")
    if yesno2==-1 or yesno2==False:
      mylist=live_archive.get_channels_with_archive(update=False, callback=None)
    elif yesno2:  
      mylist=live_archive.get_channels_with_archive(update=True, callback=showProgressUpdate)
    else:
      return
    for channel in mylist:
      live_archive.get_simple_epg(channel_stream_id=channel['channel_stream_id'], channel_name=channel['channel_name'], update=True, callback=showProgressUpdate)
  else:
    mylist=live_archive.get_channels_with_archive(update=False, callback=None)

  # Set plugin category. It is displayed in some skins as the name
  # of the current section.
  xbmcplugin.setPluginCategory(_HANDLE, 'Livestreams with archive')
  # Set plugin content. It allows Kodi to select appropriate views
  # for this type of content.
  xbmcplugin.setContent(_HANDLE, 'videos')
  # Iterate through categories
  for channel in mylist: # ['category_name', 'category_id']
    name=channel['channel_name']
    id=channel['channel_stream_id']
    thumb=channel['thumb']
    
    log("channel data: " + str(channel))

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=name)
    list_item.setInfo('video', {'title': name,
                                'set': name,
                                'mediatype': 'video'})
    list_item.setArt({'thumb': thumb, 'icon': thumb})
    uCategory=name #.encode('utf-8')
    log(u'###uCategory='+uCategory)

    url = get_url(action='live_archive_epg', category_id=id, category=uCategory)
    
    log(u'###url='+url)
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_HANDLE)

  pass

def list_channel_epg_infos(channel_stream_id):
  """
  Create the list of EPG infos in the Kodi interface.
  """
  global live_archive
  global myclient
  mylist=live_archive.get_simple_epg(channel_stream_id, "", update=False)

  # Set plugin category. It is displayed in some skins as the name
  # of the current section.
  xbmcplugin.setPluginCategory(_HANDLE, 'Archive Collection')
  # Set plugin content. It allows Kodi to select appropriate views
  # for this type of content.
  xbmcplugin.setContent(_HANDLE, 'videos')
  # Iterate through categories
  for epg in mylist: # ['category_name', 'category_id']
    name=epg['start'] +" " + epg['title']
    description=epg['description']
    id=epg['channel_stream_id']
    start=epg['start'] # .replace(' ', '%20') # done by client code 
    end=epg['end']
    duration=epg['duration']
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=name, label2=start+ " " + end)
    list_item.setInfo('video', {'title': name,
                                'set': name,
                                'mediatype': 'video',
                                'plot':description})
    list_item.setProperty('IsPlayable', 'true')
    list_item.setProperty('ResumeTime', '0.0')
    streamurl=myclient.play_timeshift(id, start, duration)

    u=streamurl.replace('%3A',':')
    u=u.replace('%2F','/')
    u=u.replace('%3F','?')
    u=u.replace('%3D','=')
    u=u.replace('%26','&')
    u=u.replace('%2020','%20')
    log("live_archive_xbmc: play url is: "+u)
    
    url = get_url(action='play', video=streamurl)
    
    is_folder = False
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_HANDLE)
  pass