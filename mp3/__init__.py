#!/usr/bin/env python

import core

from mp3server import *

class MP3Router(core.Router):#f
    dispatch = [
        (r'^/mp3/$',                                        Mp3Server()), 
        (r'^/mp3/(login\.xhtml)$',                          core.FileServer('/web/html', 'application/xhtml+xml')),
        (r'^/mp3/(mp3\.xhtml)$',                            AuthFileServer('/web/html', 'application/xhtml+xml')),
        (r'^/mp3/(.*\.swf)$',                               AuthFileServer('/web/swf', 'application/x-shockwave-flash')),
        (r'^/mp3/(.*\.js)$',                                AuthFileServer('/web/js', 'application/javascript')),
        (r'^/mp3/(.*\.css)$',                               AuthFileServer('/web/css', 'text/css')),
        (r'^/mp3/(.*\.png)$',                               AuthFileServer('/web/images', 'image/png')),
        (r'^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.mp3$',            TrackDownload()),
        (r'^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.json$',           TrackInfo()),
        (r'^/mp3/(.+)/(.+)/([0-9]+)/(.+)\.jpg$',            TrackCover()),
        (r'^/mp3/(.+)/(.+)\.zip$',                          AlbumDownload()),
        (r'^/mp3/(.+)/(.+)\.json',                          AlbumInfo()),
        (r'^/mp3/mp3\.json$',                               Artists()), # fuck artists named mp3
        (r'^/mp3/(.+)\.json$',                              ArtistInfo()), 
        (r'^/mp3/$',                                        Login())
    ]

app = MP3Router()

if __name__ == '__main__':
    core.run_server(app)

