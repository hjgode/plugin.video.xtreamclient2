# plugin.video.xtreamclient2
A Kodi Xtream Demo Client

v2.4.4 works on Kodi 19
v2.4.5 works on Kodi 18

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
  
## context.xtreamdownload:

0.7.3:
    initial release

0.7.4:
    corrected settings.xml, added category label
