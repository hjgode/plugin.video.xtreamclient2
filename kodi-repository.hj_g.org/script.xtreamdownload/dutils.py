# -*- coding: utf-8 -*-
#for python2
# Module: dutils
# version 0.0.2
# Author: HJ_G.
# Created on: 30.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import xbmc
import xbmcaddon
import xbmcgui
import re
import socket

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path') #.decode('utf-8')
sys.path.append(CWD)

def get_download_path():
  p=ADDON.getSetting('sett_downpath')
  return p

def replaceuglychars(filename):
  uglyfilechars=r'[\[\]\'\{\},;:+"\\/:"*?<>\|]+'
  newstr=re.sub(uglyfilechars, "_", filename)
  return newstr

def getHost():
  return "localhost"

def getPort():
  return 32001

def getSOCKET():
  return (getHost(), getPort())

def getSOCKETOPTION():
  return (socket.AF_INET, socket.SOCK_STREAM)