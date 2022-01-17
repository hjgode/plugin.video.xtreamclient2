# -*- coding: utf-8 -*-
#for python2
# Module: script.xtreamdownload
#         service.py
# version 0.0.3
# Author: HJ_G.
# Created on: 07.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html


import os
import sys
import threading
import socket
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

if sys.version_info[0] == 2:
    from urlparse import parse_qsl
    from urllib import quote
    from urllib2 import Request
    import urllib2
else:
    from urllib.parse import urlencode, parse_qsl, quote
    from urllib import request as Request
    import urllib


import time
import dutils
from database import Database

#global
LOGLEVEL=None

def log(s):
  global LOGLEVEL
  if LOGLEVEL==None:
    try:
      LOGLEVEL=xbmc.LOGNOTICE
    except:
      LOGLEVEL=xbmc.LOGINFO
  xbmc.log("service xtreamdownload: " + s, LOGLEVEL)

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
CWD = ADDON.getAddonInfo('path')

class Download_Queue:
  def __init__(self):
      self.db_path=os.path.join(CWD, '')
      log("using db_path: " + self.db_path)
      self.queue=[]
      self.lock=threading.Lock()
      self.abort=False
      self.downpath=dutils.get_download_path()
      log("Settings downpath: " + self.downpath)
      self.downloadthread=None
      self.download_ok=False
      pass

  def add(self, title, stream):
    item={}
    item['title']=title
    item['stream']=stream
    self.lock.acquire()
    self.queue.append(item)
    database=Database(self.db_path)
    database.add_item(item['title'], item['stream'])
    database._close_db()
    self.save()
    self.lock.release()

  def shownotification(self, title="Xtreamdownload", message=""):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title,message, 1000, None))

  def process_queue(self):
    len_queue=len(self.queue)
    if len_queue==0:
#      log('nothing in queue')
      return
    self.lock.acquire()
    task=self.queue.pop()
    log('downloading: '+task['stream']+' to ' + task['title'])
    filename=task['title']
    if not filename.endswith('.mkv'):
      log("added extension .mkv")
      filename=filename+'.mkv'
    else:
      log("no extension added")
    filepath=self.downpath
    if not filepath.endswith('/'):
      filepath=filepath+"/"
    log("filepath now: " + filepath)
    filename=dutils.replaceuglychars(filename)
    fullname=filepath+filename
    log("downloading to: "+fullname)
    self.shownotification('Xtreamdownload '+str(len_queue), 'download '+filename + ' to ' + fullname)
    #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('Downloading',fullname, 5000, None))
    mystream=task['stream']
    
    self.download_ok=False
    self.downloadthread=threading.Thread(target=self.httpdownload, args=[mystream, fullname])
    self.downloadthread.setName('downloader_thread')
    self.downloadthread.setDaemon(True) # make this terminate with the service
    self.downloadthread.start()
    while self.downloadthread.is_alive() and not self.abort:
      self.downloadthread.join(1)
      xbmc.sleep(500)
    if not self.abort:
      self.shownotification(message="download thread ended")
    else:
      self.shownotification(message="download thread aborted")
    
    self.lock.release()
    if self.download_ok:
      database=Database(self.db_path)
      database.remove_item(mystream)
      database._close_db()
    log('download done')
    self.shownotification("Xtreamdownload", "Finished: " + task['title'])
    pass

  def httpdownload(self, url, full_file_name):
    USERAGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8"
          
    if sys.version_info[0] == 2:
        url = urllib2.Request(url)
    else:
        url = urllib.request.Request(url)
        
    url.add_header("User-Agent", USERAGENT)  

    if sys.version_info[0] == 2:
      u = urllib2.urlopen(url, timeout=2)
    else:
      u = urllib.request.urlopen(url, timeout=2)
    #remove unsupported symbols from file name
    full_file_name = xbmc.makeLegalFilename(full_file_name)  
    f = open(full_file_name, 'wb')
    meta = u.info()
    if sys.version_info[0] == 2:
      file_size = int(meta.getheaders("Content-Length")[0])
    else:
      file_size = int(meta.get("Content-Length"))
    log ("Downloading: %s Bytes: %s" % (full_file_name, file_size))
    self.shownotification(message=("Downloading: %s Bytes: %s" % (full_file_name, file_size)))
    file_size_dl = 0
    block_sz = 1024*1024*10 # 10MB
    aborted=False
    if sys.version_info[0]==2:
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
          self.shownotification(message="download finished")
          break
        time_difference = end - start
        speed=round(len(buffer)/time_difference/1000)
        file_size_dl += len(buffer)
        f.write(buffer)
        f.flush()
        percent_done=int(file_size_dl * 100. / file_size)
        status = r"%10d  [%3.2f%%] " % (file_size_dl, percent_done) + "("+str(speed)+")"
        status = status + chr(8)*(len(status)+1)
        sspeed="%5i%%    %5.2f" % (percent_done, speed)
        #dlg.update(percent=percent_done, line3=sspeed)
        self.shownotification(message="downloaded "+ sspeed)
        if self.abort: # dlg.iscanceled():
          #TODO: or just remove partial file?
          #if xbmcgui.Dialog.yesno("Xtream download", "Delete partial file {}?".format(outpath)):
          os.remove(full_file_name)
          self.shownotification(message="abort. File removed!")
          break
    except myHttpError as e: # urllib2.HTTPError as e:
        self.shownotification (message="HTTP Error: " + e.code +", " + url)
        aborted=True
    except myUrlError as e:
        self.shownotification (message="URL Error: " + e.reason +", " + url)
        aborted=True
    if aborted:
        self.shownotification(message="Download FAILED!")
        #dlg.update(line3="Download failed")
    f.close()

  def save(self):
    #save to disk or sql?
    pass

  def stop(self):
    if self.lock.locked():
      log('queue locked!')
      self.abort=True
    self.save()
  pass

class Service_Thread(threading.Thread):
    def __init__(self):
        #self.SOCKET = os.path.join(CWD,'lockfile')# '/var/run/service.xtreamclient2.sock'
        self.SOCKET= dutils.getSOCKET() # ('localhost', 32001)
        threading.Thread.__init__(self)
        self.init()
        self.download_queue=Download_Queue()
    
    def init(self):
        try:
          if os.path.exists(self.SOCKET):
              os.remove(self.SOCKET)
        except:
          log("Using AF_UNIX socket")
        self.daemon = True
        #self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.sock.settimeout(2)
        #self.sock.bind(self.SOCKET)
        self.sock.bind(self.SOCKET) # "localhost",32001))
        self.sock.listen(1)
        self.stopped = False

    
    def run(self):
        #if oe.read_setting('libreelec', 'wizard_completed') == None:
        #    threading.Thread(target=oe.openWizard).start()
        #TEST: self.download_queue.add("mytitle", "mystream")
        while self.stopped == False:
            self.download_queue.process_queue()
            #self.sock.settimeout(2)
            try:
              conn, addr = self.sock.accept()
              message = (conn.recv(1024)).decode('utf-8')
              conn.close()
              if message != None:
                log('Received {message}')
                if message == 'openConfigurationWindow':
                  log(message)
                if message.startswith('start='):
                  log('got download start message')
                  log(message)
                  message=message[len("start="):] #remove start=
                  log('cleaned='+message)
                  params = dict(parse_qsl(message))
                  for p in params:
                    log(params[p])
                  self.download_queue.add(params['name'], params['stream'])
                if message == 'exit':
                    log('Exit, self.stopped')
                    self.download_queue.stop()
                    self.stopped = True
            except socket.timeout as e:
              #log("socket recv() timed out...")
              if e!=None:
                log(str(e))
            except socket.error as e:
              log("socket.error: ")
              if e != None:
                log(str(e))
            except Exception as e:
              log("Exception in sock.accept()")
              if e != None:
                log(str(e))

    def sock_send(self, message):
        #sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.SOCKET)
        sock.send(message.encode('utf-8'))
        sock.close()

    def stop(self):
        self.sock_send('exit')
        self.join()
        self.sock.close()
        try:
          if os.path.exists(self.SOCKET):
              os.remove(self.SOCKET)
        except:
          log("Service thread using TCP socket")

class Monitor(xbmc.Monitor):

    
    def onScreensaverActivated(self):
        log('onScreensaverActivated')

    
    def onDPMSActivated(self):
        log('onDPMSActivated')

    
    def run(self):
        log('Starting xtreamclient2 service thread')
        service_thread = Service_Thread()
        service_thread.start()
        while not self.abortRequested():
            if self.waitForAbort(60):
                #do some stuff
                break
        service_thread.stop()


if __name__ == '__main__':
    Monitor().run()
