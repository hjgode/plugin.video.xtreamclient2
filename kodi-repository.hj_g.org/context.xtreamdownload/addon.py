# -*- coding: utf-8 -*-
#for python2/3
# Module: context.xtreamdownload
#         addon.py
# version 0.0.8
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import xbmc
import xbmcaddon
import xbmcgui
import time
import re
import sys
import cutils
import xbmcvfs

isPython2=None
def get_is_python2():
  global isPython2
  if isPython2==None:
    if sys.version_info[0]==2:
      isPython2=True
    else:
      isPython2=False
  return isPython2
get_is_python2()

if isPython2:
    from urlparse import parse_qsl
    from urllib import quote
    from urllib2 import Request
    import urllib2
else:
    from urllib.parse import urlencode, parse_qsl, quote
    from urllib import request as Request
    import urllib

addon = xbmcaddon.Addon()    
folder = addon.getSetting("folder")


def _mydecodeHTML(url):
  s=url.replace("http%3A%2F%2F", "http://")
  s=s.replace("%2F","/")
  s=s.replace("%3A",":")
  return s

def getplayurl(splaypath):
  """  test_path_string=
        "plugin://plugin.video.xtreamclient2/?action=play&video=http%3A%2F%2Fsever.xyz%3A8080%2Fplay%2FYG7lSWcYcEph46xPtEwsJ6n5A8pyB-FN6dXxQMOmKcIYdZrTDrbaXSDnHVf9RLgs" 
      return: 
        http://server.xyz:8080/play/YG7lSWcYcEph46xPtEwsJ6n5A8pyB-FN6dXxQMOmKcIYdZrTDrbaXSDnHVf9RLgs
  """
  myurl=None
  match=re.match(r".*=play&video=(?P<url>.*)", splaypath)
  if match:
    myurl=match.group('url')
    myurl=_mydecodeHTML(myurl)
  return myurl

def log(msg):
  addon = xbmcaddon.Addon()
  addonID = addon.getAddonInfo('id')
  try:
    xbmc.log('%s: %s' % (addonID, msg), xbmc.LOGNOTICE) 
  except:
    xbmc.log('%s: %s' % (addonID, msg), xbmc.LOGINFO)
    
def replaceuglychars(filename):
  uglyfilechars=r'[\[\]\'\{\},;:+"\\/:"*?<>\|]+'
  newstr=re.sub(uglyfilechars, "_", filename)
  return newstr

def httpdownload(url, file_name):
  global folder
  log("Entering httpdownload with: " + file_name)
  log("folder is: " +folder)
  USERAGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8"

  file_name=replaceuglychars(file_name)
  log("replaceuglychars returned: " + file_name)  

  if not file_name.endswith(".mkv"):
    file_name=file_name+".mkv"
  outpath = os.path.join(folder, file_name)   
  log("outpath= " + outpath)

  dialog = xbmcgui.Dialog()

  #Error Contents: 'ascii' codec can't encode character '\xf6' in position 36: ordinal not in range(128)
  #title (file name) is returned as utf-8 by Kodi 19?
  if not xbmcvfs.exists(folder):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Xtream download', "Download path '{}'does not exist. Create new??".format(folder))
    if ret:
      os.mkdir(folder)
    else:
      return

  if xbmcvfs.exists(outpath):
    dialog = xbmcgui.Dialog()
    ret=dialog.yesno("Xtream download", "File {} already exists. Overwrite?".format(file_name))
    if not ret:
      return

  log("create file: " + outpath)
  try:
    log("type of outpath: " + str(type(outpath)))
    f = xbmcvfs.File(outpath, 'wb')
  except UnicodeEncodeError as e:
    dlg = xbmcgui.Dialog()
    dlg.notification("context.xtreamdownload", "failed to create file with error: " + str(e))
    return
  except Exception as e:
    dlg = xbmcgui.Dialog()
    dlg.notification("context.xtreamdownload", "failed to create file with error: " + str(e))
    return

  log("created file: " + outpath)

  dialog = xbmcgui.Dialog()
  ret = dialog.yesno('Xtream download', "Start download of {} to {}?".format(url, outpath))
  if not ret:
    f.close()
    return

  
  if isPython2:
    url = urllib2.Request(url)
  else:
    url = urllib.request.Request(url)

  #url = urllib2.Request(url)
  url.add_header("User-Agent", USERAGENT)  

  if isPython2:
    u = urllib2.urlopen(url, timeout=2)
  else:
    u = urllib.request.urlopen(url, timeout=2)

  #u = urllib2.urlopen(url)
  
  meta = u.info()
  if isPython2:
    file_size = int(meta.getheaders("Content-Length")[0])
  else:
    file_size = int(meta.get("Content-Length"))
  #file_size = int(meta.getheaders("Content-Length")[0])
  print ("Downloading: %s Bytes: %s" % (outpath, file_size))

  file_size_dl = 0
  block_sz = 1024*1024*10 # 10MB
  dlg=xbmcgui.DialogProgress()
  xbmcversioninfo=cutils.get_installed_version()
  log("xbmc versioninfo=" + str(xbmcversioninfo))
  # xbmc versioninfo={'major': 19, 'minor': 0, 'revision': '20210219-f44fdfbf67', 'tag': 'stable'}
  if xbmcversioninfo['major']<=18:
    #in kodi 18 with python2 we had up to three lines plus the heading
    dlg.create( heading="Xtream download", line1="Downloading "+str(file_size)+" bytes", line2="File: "+outpath)
  else:
    # Kodi 19 only has heading= and message=, no more lineX 
    dlg.create( "Xtream download", "Downloading "+str(file_size)+" bytes, File: "+outpath)
  aborted=False
  if isPython2:
    myHttpError = urllib2.HTTPError
    myUrlError = urllib2.URLError
  else:
    myHttpError = urllib.error.HTTPError
    myUrlError = urllib.error.URLError
  try:
    while True:
      start = time.time()
      buffer = u.read(block_sz)
      end = time.time()
      if not buffer:
        if isPython2:
          dlg.update(percent=100,line3="Done")
        else:
          dlg.update(percent=100, message="Done")
        break
      time_difference = end - start
      speed=round(len(buffer)/time_difference/1000)
      file_size_dl += len(buffer)
      f.write(buffer)
      #f.flush() # xbmcvfs File has no flush()
      percent_done=int(file_size_dl * 100. / file_size)
      status = r"%10d  [%3.2f%%] " % (file_size_dl, percent_done) + "("+str(speed)+")"
      status = status + chr(8)*(len(status)+1)
      sspeed="%5i%%    %5.2f" % (percent_done, speed)
      if isPython2:
        dlg.update(percent=percent_done, line3=sspeed)
      else:
        dlg.update(percent=percent_done, message= "Downloading "+str(file_size)+" bytes, File: "+outpath +"\n" + sspeed)
      if dlg.iscanceled():
        dlg.close()
        if dialog.yesno("Xtream download", "Delete partial file {}?".format(outpath)):
          os.remove(outpath)
        break
  except myHttpError as e:
      log ("HTTP Error: " + e.code +", " + url)
      aborted=True
  except myUrlError as e:
      log ("URL Error: " + e.reason +", " + url)
      aborted=True
  if aborted:
    if isPython2:
      dlg.update(line3="Download failed")
    else:
      dlg.update(message="Download failed")
      
  if dlg!=None:
    time.sleep(3)
    dlg.close()
  f.close()

#MAIN    

#xbmcgui.ListItem
path = sys.listitem.getPath()
title = sys.listitem.getLabel()
log('clicked on: '+ title+ ' / ' + path)
"""
clicked on: 
Autopsie - Mysteriöse Todesfälle - S01E01 - Die Bestie von Oak Cliff u.a.
 / 
plugin://plugin.video.xtreamclient2/?action=play&video=http%3A%2F%2Fsero-team.xyz%3A8080%2Fplay%2F28gXuXPqitBI-
"""
"""
2021-12-26 08:58:07.185 T:1436541824  NOTICE: context.downloadit: clicked on: Sh
in Godzilla (2016), plugin://plugin.video.xtreamclient2/?action=play&video=http%
3A%2F%2Fserver.xyz%3A8080%2Fplay%2FYG7lSWcYcEph46xPtEwsJ6n5A8pyB-FN6dXxQMOmKc
IYdZrTDrbaXSDnHVf9RLgs
"""
#log(repr(title))

# start video
kodi_player = xbmc.Player()
kodi_player.play(path, sys.listitem)
time.sleep(10) 
videoda=0

# until the first file is played read file
while videoda==0 :
    try:
        file=kodi_player.getPlayingFile()
        log("-----> "+file)
        if not file=="":
            videoda=1
    except:
        pass 

kodi_player.stop()
log("KodiPlayer playing file: "+file)
"""
2021-12-27 15:00:26.356 T:140394876626688  NOTICE: context.xtreamdownload: '96 H
ours - Taken 3 (2014)'
2021-12-27 15:00:27.363 T:140395496819904  NOTICE: VideoPlayer::OpenFile: plugin
://plugin.video.xtreamclient2/?action=play&video=http%3A%2F%2Fserver.xyz%3A80
80%2Fplay%2FYG7lSWcYcEph46xPtEwsJ6n5A8pyB-FN6dXxQMOmKcK_1i92hcSaTijV2nl2xPh7
"""
url=file
log("downloadfile: "+url+", "+ title)
newurl=_mydecodeHTML(url)
log("newurl= " + newurl)
httpdownload(newurl,title)
