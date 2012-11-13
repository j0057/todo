import json
import os, os.path
import re
import StringIO
import zipfile

import webob
import webob.exc

import mutagen
import mutagen.mp3

from jjm import core

class authorized(core.BaseDecorator):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args):
        if request.session is None:
            raise webob.exc.HTTPFound(location='/mp3/login.xhtml?url=' + request.path)

        if 'MP3' not in request.session.rights:
            raise webob.exc.HTTPFound(location='/mp3/login.xhtml?url=' + request.path)

        return self.func(request, *args)

class LibraryModel(object):
    def __init__(self, library):
        self._library_name = library
        self._library = None
        self._library_time = 0
        self._library_client = None

    def _load_library(self):
        with open(self._library_name, 'r') as f:
            self._library = json.load(f)
            self._library_time = os.stat(self._library_name).st_mtime

    def _gen_library_client(self):
        self._library_client = dict(
            (artist, dict(
                (album, 
                    dict(
                        ('{0:02}'.format(int(track)), self.library[artist][album][track]['name'])
                        for track in self.library[artist][album]))
                for album in self.library[artist]))
            for artist in self.library)

    def _get_library(self):
        if not self._library:
            self._load_library()
        return self._library
    library = property(_get_library)

    def _get_library_client(self):
        if self._library_time < os.stat(self._library_name).st_mtime:
            self._library = None
            self._library_client = None
            self._library_time = 0
        if not self._library_client:
            self._gen_library_client()
        return self._library_client
    library_client = property(_get_library_client)

class Model(object):
    def __init__(self, library):
        self.library = LibraryModel(library)

class Artists(core.Resource):
    #authorized
    @core.transformer
    def GET(self, request):
        if 'lazy' in request.GET and request.GET['lazy'] == 'true':
            return 200, 'application/json', sorted(MODEL.library.library_client.keys())
        else:
            return 200, 'application/json', MODEL.library.library_client

class ArtistInfo(core.Resource):
    @core.transformer
    def GET(self, request, artist):
        if 'lazy' in request.GET and request.GET['lazy'] == 'true':
            return 200, 'application/json', sorted(MODEL.library.library_client[artist].keys())
        else:
            return 200, 'application/json', MODEL.library.library_client[artist]

class AlbumInfo(core.Resource):
    @core.transformer
    def GET(self, request, artist, album):
        if 'lazy' in request.GET and request.GET['lazy'] == 'true':
            return 200, 'application/json', sorted(MODEL.library.library_client[artist][album].keys())
        else:
            return 200, 'application/json', MODEL.library.library_client[artist][album]

class TrackInfo(core.Resource):
    #authorized
    @core.transformer
    def GET(self, request, artist, album, track, title):
        fn = MODEL.library.library[artist][album][track]['fn'].encode('utf8');
        id3 = mutagen.mp3.MP3(fn)
        cover = None
        mime = None
        if 'APIC:' in id3:
            mime = id3['APIC:'].mime
            #cover = '/mp3/tracks/{0}/{1}/{2}/{3}.jpg'.format(artist, album, track, title)
        return 200, 'application/json', {
            'artist':artist,
            'album':album,
            'track':track,
            'title':title,
            'cover':mime}

class TrackCover(core.Resource):
    @core.transformer
    def GET(self, request, artist, album, track, title):
        filename = MODEL.library.library[artist][album][track]['fn'].encode('utf8')
        id3 = mutagen.mp3.MP3(filename)
        if 'APIC:' in id3:
            return 200, str(id3['APIC:'].mime), id3['APIC:'].data
        else:
            return 404, 'text/plain', 'No cover'

class TrackDownload(core.Resource):
    @core.partial
    def GET(self, request, artist, album, track, title):
        filename = MODEL.library.library[artist][album][track]['fn'].encode('utf8')
        filesize = os.stat(filename).st_size
        response = webob.Response(content_type='audio/mpeg')
        response.body_stream = open(filename, 'rb')
        response.content_length = filesize
        response.headers['X-Accel-Limit-Rate'] = str(50 * 1024);
        return response

class AlbumDownload(core.Resource):
    @core.partial
    @core.cached(8)
    def GET(self, request, artist, album):
        core.debug(request, 'download {0} {1}'.format(repr(artist), repr(album)))
        albuminfo = MODEL.library.library[artist][album]
        filenames = [ albuminfo[track]['fn'] for track in sorted(albuminfo.keys(), key=int) ]
        buf = StringIO.StringIO()
        zf  = zipfile.ZipFile(buf, 'w')
        for fn in filenames:
            artist = re.sub(r'[\/:*?<>|]', '_', artist)
            album = re.sub(r'[\/:*?<>|]', '_', album)
            arcname = u'{0} - {1}/{2}'.format(artist, album, os.path.basename(fn));
            core.debug(request, repr(os.path.basename(fn)))
            core.debug(request, repr(arcname))
            zf.write(fn.encode('utf8'), arcname=arcname.encode('windows-1252'), compress_type=zipfile.ZIP_STORED)
        zf.close()
        result = webob.Response(content_type='application/zip', content_length=len(buf.getvalue()))
        result.body_stream = buf
        buf.seek(0)
        return result

class Login(core.Resource):
    def POST(self, request):
        users = ((core.ini.auth['username{0}'.format(i)],
                  core.ini.auth['password{0}'.format(i)],
                  core.ini.auth['rights{0}'.format(i)])
                 for i in range(int(core.ini.auth.count)))
        for (u,p,r) in users:
            if request.POST['username'] != u: continue
            if request.POST['password'] != p: continue
            location = ('redirect' in request.POST) and request.POST['redirect'] or '/mp3'
            response = webob.Response(status_int=302, location=location)
            core.session.start_session(request, response)
            request.session.rights = r
            return response
        else:
            raise webob.exc.HTTPForbidden('Bad username or password.')    

class AuthFileServer(core.FileServer):
    #authorized
    def GET(self, request, filename):
        return super(AuthFileServer, self).GET(request, filename)

class Mp3Server(core.Resource):
    #authorized
    def GET(self, request):
        raise webob.exc.HTTPFound(location='mp3.xhtml')
        
MODEL = Model('/home/joost/www/mp3/mp3.json')

