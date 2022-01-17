# # -*- coding: utf-8 -*-
#for python2
# Module: xt_utils
# version 2.4.5
# Author: HJ_G.
# Created on: 19.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import xbmc
import xbmcaddon
import xbmcgui

from client import Client

if sys.version_info[0] == 2:
    import urllib
    from urlparse import parse_qsl
else:
    from urllib.parse import urlencode, parse_qsl, quote

    
# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])
# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]

# convert byte data to strings
def convert(data):
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return tuple(map(convert, data))
    return data

def log(msg, level=xbmc.LOGINFO):
  if sys.version_info[0]==3 and level==xbmc.LOGINFO:
    try:
      level=xbmc.LOGNOTICE
    except AttributeError as e:
      level=xbmc.LOGINFO
  plugin = "plugin.video.xtreamclient2"
  try:
    if isinstance(msg, unicode):
      msg = msg.encode('utf8')
  except Exception:
    msg=msg
  xbmc.log("[%s] %s" % (plugin, msg), level)
    
log(CWD)

def show_dialog(msg):
  #    dialog = xbmcgui.Dialog()
    dlg=xbmcgui.DialogProgress()
    dlg.create('Plugin', msg, '', '')
    count=5
    for i in range(count):
        dlg.update(i*20)
        xbmc.sleep(1000)
    dlg.close()    

# disable in development!
myconfig={} # cfg.config
def get_settings():
    """ return a dict with the current addon settings 
    
        Returns:
        ['url', 'username', 'password', 'port', 'filter', 'filter_is_regex:"true"|"false"']
    """
    log("get_settings...")
    global myconfig
    myconfig={}
    my_addon = xbmcaddon.Addon()
    log("get_settings addon="+str(my_addon.getAddonInfo('path')))
    #     url = cfg.config["url"] + ":" + cfg.config["port"] + "?username=" + cfg.config["username"] + "&password=" + cfg.config["password"]
    myconfig['url']=my_addon.getSetting('sett_website')
    myconfig['username']=my_addon.getSetting('sett_username')
    myconfig['password']=my_addon.getSetting('sett_password')
    myconfig['port']=my_addon.getSetting('sett_portnumber')
    myconfig['filter']=my_addon.getSetting('sett_filter')
    myconfig['filter_is_regex']=my_addon.getSetting('sett_filter_is_regex') # returns the string 'true' or 'false'
    return myconfig

myclient=None
def start_connection():
    global myconfig
    global myclient
    myconfig=get_settings()
    url = myconfig["url"] + ":" + myconfig["port"] + "?username=" + myconfig["username"] + "&password=" + myconfig["password"]
    if myclient==None:
      myclient=Client(url)
    #print(client)
    return myclient

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    if sys.version_info[0] == 2:
        return '{}?{}'.format(_URL, urllib.urlencode(kwargs))
    else:
        return '{}?{}'.format(_URL, urlencode(kwargs))

