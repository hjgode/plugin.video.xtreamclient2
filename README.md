# plugin.video.xtreamclient2
A Kodi Xtream Demo Client

v2.4.4 works on Kodi 19
v2.4.5 works on Kodi 18

starting with v 3.x.x code works on Kodi 18 and 19.

The idea was to have one code for both Kodi 18 and 19, Python 2.7 and Python 3.7. But I was unable to make this work and so we have two code lines :-(

## xtreamclient2, v2.4.9 with bug fixes and enhancements

2.4.6:
  fixed staffeln that come as list and not as dict, i.e. DE Action > Dr Who
  fixed episode listing for empty season

2.4.7:
  some code cleanup

2.4.8:
  missing enum lib

2.4.9:
  with enum.py and dependcies to urllib3 and reuests kodi python script libraries
  tested within docker/leia container

3.0.0:
  added option to download video in combination with context.xtreamdownload context addon
  added option (conext) to download stream via background script provided by script.xtreamdownload

3.0.1:
  made the code run with Kodi Matrix (Python3)

3.1.0:
  compatible with Python 2 and 3
3.2.0:
  started with database...
3.3.0:
  database update and search finished
3.3.1:
  added LiveArchive class
4.0.0:
  adding LiveArchive for XBMC: Done
  added function to show oldest and newest epg entry datetime
4.0.1:
  added Search Live Archive option
  changed addon.xml name->Xtream Plugin2 as label shows in header and was too long

## context.xtreamdownload:

0.7.3:
    initial release

0.7.4:
    corrected settings.xml, added category label

## script.xtreamdownload

unable to test with Kodi 19!

0.0.1:
    initial release. This is a service script which gets commands to download from plugin.xtreamclient2. Uses a queue and background thread to download one by one.

0.0.2:
    made code code compatible with Kodi Matrix (Python3)
