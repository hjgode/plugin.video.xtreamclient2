# -*- coding: utf-8 -*-
import requests
from requests.models import Response

from connection import Connection
from url_api_builder import EndpointEnum, Url_api_builder

class Client:
    def __init__(self, url):
        self._url = url
        self.last_error="None"
        self.matched, self._connection = Connection.from_url(url)

    def user_panel(self):
        return self._get(EndpointEnum.USER_PANEL)

    def auth(self):
        return self._get(EndpointEnum.AUTH)

    def live_streams(self):
        return self._get(EndpointEnum.LIVE_STREAMS)

    def vods(self):
        return self._get(EndpointEnum.VODS)

    def vod_categories(self):
        """return a list of category dicts with category_name and category_id

        001:{u'category_id': u'686', u'category_name': u'DE \u2022 4K Filme 2021', u'parent_id': 0}
            u'category_name':u'DE \u2022 3D Filme'
            u'parent_id':0
            len():3
            special variables
            function variables
            u'category_id':u'686'
            u'category_name':u'DE \u2022 4K Filme 2021'
            u'parent_id':0
            len():3
        """
        return self._get(EndpointEnum.VOD_CATEGORIES)
    def vod_streams_by_category(self, category):
        """ returns a list of videos with plot information etc 
            [u'direct_source', u'rating', u'rating_5based', u'stream_id', u'container_extension', 
            u'year', u'stream_icon', u'plot', u'title', u'category_ids', 
            u'episode_run_time', u'added', u'stream_type', u'director', u'genre', 
            u'youtube_trailer', u'name', u'release_date', u'cast', u'custom_sid', 
            u'num', u'category_id']

        """
        return self._get(EndpointEnum.VOD_STREAMS_BY_CATEGORY, category)

    def live_categories(self):
        """ get all live categories 
            Returns:
            dict with category id and name
        """
        return self._get(EndpointEnum.LIVE_CATEGORIES)

    def live_streams_by_category(self, category):
        return self._get(EndpointEnum.LIVE_STREAMS_BY_CATEGORY, category)

    def series_categories(self):
        return self._get(EndpointEnum.SERIES_CATEGORIES)
    def series_streams_by_category(self, category):
        return self._get(EndpointEnum.SERIES_STREAMS_BY_CATEGORY, category)
    def series_info_by_id(self, id):
        return self._get(EndpointEnum.SERIES_INFO, id)
    def series(self): #get all series
        return self._get(EndpointEnum.SERIES)

    def xmltv(self):
        return self._get(EndpointEnum.XMLTV)

    def all_epg(self, stream_id):
        return self._get(EndpointEnum.ALL_EPG, stream_id)

    def short_epg(self, stream_id, limit = 5):
        return self._get(EndpointEnum.SHORT_EPG, stream_id, limit)

    def get_simple_epg(self, stream_id):
      """ get simple epg daza (json) for stream_id 
          Returns list of dicts with base64 encoded title and description:
              "epg_listings": [
          {
            "id": 1641335700,
            "epg_id": 0,
            "channel_id": "DASERST",
            "start": "2022-01-04 23:35:00",
            "end": "2022-01-05 01:20:00",
            "lang": "de",
            "title": "RmlzaGVybWFuJ3MgRnJpZW5kcyAtIHZvbSBLdXR0ZXIgaW4gZGllIENoYXJ0cw==",
            "description": "WmVobiBzaW5nZW5kZSBNw6RubmVyIGF1cyBlaW5lbSBGaXNjaGVyZG9yZiBpbiBDb3Jud2FsbCB3ZXJkZW4gdm9tIE11c2lrcHJvZHV6ZW50ZW4gRGFubnkgKERhbmllbCBNYXlzKSBiZXN1Y2h0LCBkZXIgc2llIGbDvHIgZWluZW4gUGxhdHRlbnZlcnRyYWcgYmVpIFVuaXZlcnNhbCBnZXdpbm5lbiBtw7ZjaHRlLiBFcyBzdGVsbHQgc2ljaCBoZXJhdXMsIGRhc3MgZXMgc2ljaCBiZWkgZGVyIEFrdGlvbiBudXIgdW0gZWluZW4gU2NoZXJ6IHNlaW5lcyBDaGVmcyBoYW5kZWx0LCBtaXQgZGVyIFplaXQgZ2xhdWJ0IGRlciBzb25zdCBzbyB6eW5pc2NoZSBEYW5ueSBhbGxlcmRpbmdzIHdpcmtsaWNoIGRhcmFuLCBkYXNzIGVyIG1pdCBkZXIgQmFuZCBlaW5lbiBIaXQgcHJvZHV6aWVyZW4ga8O2bm50ZS4=",
            "start_timestamp": 1641335700,
            "stop_timestamp": 1641342000,
            "now_playing": 0,
            "has_archive": 0
          },
          {
            "id": 1641342000,

      """
      return self._get(EndpointEnum.SIMPLE_EPG, stream_id)

    def play_timeshift(self, stream_id, start, duration): 
        """ 
            get the playable archive url
            replaces chars Blank and ':'
             
            Params:
            start=2019-04-19:16-00
            duration=120 (minutes)
            start 2019-04-19 16:00:01 => 2019-04-19:16-00
        """
        start=start[:len(start)-3] # cut off seconds
        start=start.replace(':', '-')
        start=start.replace(' ',':')
        return self._get(EndpointEnum.PLAY_TIMESHIFT, stream_id, start, duration)

    def _get(self, ep, *args):
        """ returns a respones or an URL (timeshift only) """
        r = Response
        r.status_code=200
        self.last_error="None"
        try:
            url=Url_api_builder.build(ep, self._connection, *args)
            if 'timeshift' in url:
              return url
            r = requests.get(url,timeout=15)
            r.raise_for_status()
            if r.status_code==200:
                self.last_error="None (200)"
                if 'xmltv.php' in url:
                  return r.text # xml epg data?
                else:
                  return r.json()
#            return r.json() if r.status_code == 200 else None
        except requests.exceptions.Timeout as e:
            self.last_error='Timeout Error ('+str(r.status_code)+')' + ', no server answer within time.'
        except requests.exceptions.TooManyRedirects as e:
            self.last_error='TooManyRedirects Error ('+str(r.status_code)+')' + ', invalid server address?'
        except requests.exceptions.HTTPError as e:
            self.last_error='HTTP Error ('+str(r.status_code)+')' + ', invalid HTTP response.'
            print(e)
        except requests.exceptions.ConnectionError as e:
            self.last_error='ConnectionError('+str(r.status_code)+')'+', network problem: no internet, DNS, refsued connection etc.'
            print(e)
        except requests.exceptions.RequestException as e:
            self.last_error='RequestException('+str(r.status_code)+')'
            print(e)
        except Exception as e:
            self.last_error=e.__doc__ + str(r.status_code)+')'
            print(e)
        return None
#        if r.status_code ==200:
#            return r.json()
#        else:
#            return None
#        return r.json() if r.status_code == 200 else None

    def get_last_error(self):
        if self.last_error==None:
            self.last_error="unknown, see log"
        return self.last_error