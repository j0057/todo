#!/usr/bin/env python

import httplib
import re
import urllib

import core

from mp3server import *

class MP3Router(core.Router):
    dispatch = [
        (r"^/mp3/$",                                        Mp3Server()), 
        (r"^/mp3/(login\.xhtml)$",                          core.FileServer("/web/html", "application/xhtml+xml")),
        (r"^/mp3/(mp3\.xhtml)$",                            AuthFileServer("/web/html", "application/xhtml+xml")),
        (r"^/mp3/(.*\.swf)$",                               AuthFileServer("/web/swf", "application/x-shockwave-flash")),
        (r"^/mp3/(.*\.js)$",                                AuthFileServer("/web/js", "application/javascript")),
        (r"^/mp3/(.*\.css)$",                               AuthFileServer("/web/css", "text/css")),
        (r"^/mp3/(.*\.png)$",                               AuthFileServer("/web/images", "image/png")),
        (r"^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.mp3$",            TrackDownload()),
        (r"^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.json$",           TrackInfo()),
        (r"^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.jpg$",            TrackCover()),
        (r"^/mp3/(.+)/(.+)\.zip$",                          AlbumDownload()),
        (r"^/mp3/(.+)/(.+)\.json",                          AlbumInfo()),
        (r"^/mp3/mp3\.json$",                               Artists()), # fuck artists named mp3
        (r"^/mp3/(.+)\.json$",                              ArtistInfo()), 
        (r"^/mp3/$",                                        Login())
    ]

def debug(app, filter_func=None):
    def wsgi_app(env, start_response):
        def debug_start_response(status, headers):
            print
            for (k, v) in headers:
                print '> {0}: {1}'.format(k, repr(v))
            print
            start_response(status, headers)
        if filter_func != None and filter_func(env['REQUEST_URI']):
            keys = sorted(k for k in env.keys()
                          if k.startswith('HTTP_') 
                          or k.startswith('REQUEST_') 
                          or (k == 'QUERY_STRING') 
                          or (k == 'SERVER_PROTOCOL'))
            print
            for k in keys:
                print '< {0}: {1}'.format(k, repr(env[k]))
            print
            result = app(env, debug_start_response)
        else:
            result = app(env, start_response)
        return result
    return wsgi_app

app = MP3Router()
app = debug(app, filter_func=lambda uri: uri.startswith('/mp3') and uri.endswith('.mp3'))

if __name__ == "__main__":
    try:
        core.run_server(app)
    except KeyboardInterrupt:
        pass

