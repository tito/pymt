# FlickrClient
# Copyright (c) 2004 Michele Campeotto

import xmltramp
import sys

from urllib import urlencode


HOST = 'http://flickr.com'
PATH = '/services/rest/'
API_KEY = '2a02cfc894c73bac3cc167e1d2333ce2'



class FlickrError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Flickr Error %s: %s' % (self.code, self.message)


class FlickrClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def __getattr__(self, method):
        def method(_self=self, _method=method, **params):
            _method = _method.replace("_", ".")
            url = HOST + PATH + "?method=%s&%s&api_key=%s" % \
                    (_method, urlencode(params), self.api_key)
            try:
                    rsp = xmltramp.load(url)
            except:
                    return None
            return _self._parseResponse(rsp)
        return method

    def _parseResponse(self, rsp):
        if rsp('stat') == 'fail':
            raise FlickrError(rsp.err('code'), rsp.err('msg'))

        try:
                return rsp[0]
        except:
                return None


user = None
photoSets = None
