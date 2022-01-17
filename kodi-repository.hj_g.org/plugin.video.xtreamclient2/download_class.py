# # -*- coding: utf-8 -*-
# vod xtream API
# Module: downloader_class
# Author: HJ_G.
# Created on: 28.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
#


class Downloader:
  def __init__(self):
    self.logging=True
    pass
  def add_download(self, name, http_stream):
    self._log ('Download added: ' + name + " > " + http_stream)
    pass
  def _log(self, msg):
    if not self.logging:
      return
    plugin = "plugin.video.xtreamclient: Downloader class"
    print("[%s] %s" % (plugin, msg.__str__()))
pass
