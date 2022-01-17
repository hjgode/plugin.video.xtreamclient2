# # -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
# version 0.0.1
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import os
import socket
import dutils

if sys.version_info[0] == 2:
    import urllib
    from urlparse import parse_qsl
else:
    from urllib.parse import urlencode, parse_qsl, quote
#import urllib
#from urlparse import parse_qsl

import xbmc
import xbmcgui
import xbmcaddon

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path')


def log(s):
    if sys.version_info[0] == 2:
      xbmc.log("script.xtreamdownload: default.py: " + s, xbmc.LOGNOTICE)
    else:
      xbmc.log("script.xtreamdownload: default.py: " + s, xbmc.LOGINFO)

if __name__ == '__main__' :
    log(ADDON.getAddonInfo('id'))
    args=sys.argv
    #sys.argv[0] is name of xbmc script
    for a in args:
      log(a) # name=... and stream=...
    """2021-12-29 10:34:00.939 T:140079631361792  NOTICE: script.xtreamdownload
      2021-12-29 10:34:00.939 T:140079631361792  NOTICE: default.py
      2021-12-29 10:34:00.939 T:140079631361792  NOTICE: ?name=96%20Hours%20%282008%29...
    """
    if len(sys.argv)!=2:
      quit()
    #sys.argv[1] is name of python file
    log('sys.argv[1] is: ' + sys.argv[1])
    #parse_qsl will also uncode html entyities
    params = dict(parse_qsl(sys.argv[1][1:]))
    for p in params:
      log(p + "=" + params[p])
    
    #FIXME
    #SOCKET = os.path.join(CWD,'lockfile')# '/var/run/service.xtreamclient2.sock'
    for i in range(3):
      try:
        log("getSOCKET()..." + str(i))
        SOCKET= dutils.getSOCKET() # ('localhost',32001)
        #sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        log("getSOCKETOPTIONS()..." + str(i))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        log("socket.connect()..." + str(i))
        sock.connect(SOCKET)
        log("socket.send()...")
        sock.send( ('start='+ sys.argv[1][1:]).encode('utf-8'))
        log("socket.close()...")
        sock.close()
        log("socket send and close OK")
        break
      except socket.timeout as e:
        #log("socket recv() timed out...")
        if e!=None:
          log(str(e))
      except socket.error as e:
        log("socket.error: ")
        if e != None:
          log(str(e))
      except Exception as e:
        if e != None:
          log("Exception in socket communication! "+ str(e))
      xbmc.sleep(1000)
