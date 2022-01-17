# -*- coding: utf-8 -*-
#for python2
# Module: main
# version 2.4.5
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

"""
#TODO:
  add search dialogs
  router params             show dialog
  action="search"           Input Dialog for search term (being used as arg in LIKE '%searchterm%')
  action="searchoptions"    show dialog to select search area (Live, Series, VOD or All)
  action="searchresults"    show normal list of videos and series titles found for search term
  
"""
#for utf-8 and python3 compatibility
from __future__ import unicode_literals
from __future__ import print_function
import sys
if sys.version_info[0]==2:
  reload(sys)
  sys.setdefaultencoding('utf8')

if sys.version_info[0] == 3:
    # Python 3: 
    from urllib.parse import urlencode, parse_qsl
else:
    import urllib
    from urlparse import urlparse
    from urlparse import parse_qsl
    import re
    

try:
  import xbmc
  print ("No Testing, running with xbmc")
  from xtutils import start_connection, get_settings, get_url
  #from xtutils import *
  import xbmcgui
  import xbmcplugin
  import xbmcaddon
except Exception as e:
  print ("Testing environent, running without xbmc")
  from xtutils_test import start_connection, get_settings, get_url

#TODO: remove for release
#import web_pdb
#TODO: remove for release
#web_pdb.set_trace()


# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)

#from xtutils import start_connection, get_settings
from database_update import Update_DB

#for development use this
#import xtreamcode_config as cfg

def log(msg):
    try:
      level=xbmc.LOGNOTICE
    except:
      level=xbmc.LOGINFO
    plugin = "plugin.video.xtreamclient SEARCH"
    xbmc.log("[%s] %s" % (plugin, msg.encode('utf8')), level)

def showSearchInput():

  pass

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

def showSearchOptions():
  log('Entering Xtream SearchOptions...')
  optionlist=["Live", "Series", "Video", "All"]
  """ show selection for either Live (0), Series (1), VOD (2) or All (3)"""
  dlg=xbmcgui.Dialog()
  selected=dlg.select("Select area for Search", optionlist)
  if selected==-1:
    return
  dlg=xbmcgui.Dialog()
  do_update=dlg.yesno("Database", "Update data in " + optionlist[selected] +"?")
  if do_update==-1:
    return
  update_db = Update_DB(CWD)
  if do_update:
    log('updating database')
    showProgress('Updating database',0)
    if selected==3:
      update_db.cleanTable()  # clean all
      update_db.updateLive(showProgressUpdate)
      update_db.updateSeries(showProgressUpdate)
      update_db.updateVOD(showProgressUpdate)
    else:
      update_db.cleanTable(selected)
      if selected==0:
        update_db.updateLive(showProgressUpdate)
      elif selected==1:
        update_db.updateSeries(showProgressUpdate)
      elif selected==2:
        update_db.updateVOD(showProgressUpdate)
    showProgress("update finished", 100, update=True, close=True)
    log("db update finished")

  log("Selected Option: " + str(selected))
  input=dlg.input("Enter Search term", "", xbmcgui.INPUT_ALPHANUM)
  if len(input)==0:
    return
  #now start a search
  showProgress(input, 0)
  showProgress(input, 100, update=True)
  if selected==3:
    selected=None
  rows=update_db.find(input, selected)
  showProgress('found ' + str(len(rows)) + ' for ' + input, 0, update=True, close=True )
  
  xbmcplugin.setContent(_HANDLE, 'videos')
  for row in rows:
    name=row[1]
    video=row[4]
    category_name=row[3]
    category_id=row[2]
    series_id=row[5]
    thumb=row[7]

    log(row[1] + " " + row[4]) # 1=name 4 = stream
    if len(series_id)>0:
      label2=category_name + "/" + series_id 
    else:
       label2=category_name
    list_item=xbmcgui.ListItem(label=name, label2=category_name + "/" + series_id)
    list_item.setInfo('video', {'title': name,
                                'genre': category_name,
                               'mediatype': 'video'})    
    if len(video)>0:
      list_item.setProperty('IsPlayable', 'true')
      is_folder=False
      url = get_url(action='play', video=video)
    else:
      list_item.setProperty('IsPlayable', 'false')
      is_folder=True
      url = get_url(action='list_seasons_in_serie', serie_id=series_id, serie_name=name, category_name=category_name)
    if(len(thumb)>0):
      list_item.setArt({'thumb': thumb, 'icon': thumb})

    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

  showProgress('found ' + str(len(rows)) + ' for ' + input, 0, update=True, close=True )
  xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_GENRE )
  xbmcplugin.endOfDirectory(_HANDLE)

  pass

def showSearchResults():
  pass

# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])


if __name__ == '__main__':
    print ('#### %s args ####' % ADDON.getAddonInfo('id'))
    for a in sys.argv:
      print (a)
    
    
