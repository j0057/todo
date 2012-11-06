#!/usr/bin/env python

import json
import os
import re

from itertools import groupby

import mutagen
import mutagen.id3
import mutagen.mp3

from unidecode import unidecode

import core.sh

mutagen.id3.pedantic = False

__all__ = [ 'Track', 'TrackList', 'Library' ]

def _clean_url(name, s="-"):
    name = name.lower()
    name = unidecode(name)
    name = name.replace('\'', '')
    name = re.sub('[^a-z0-9+]+', s, name)
    name = re.sub('^' + s, '', name)
    name = re.sub(s + '$', '', name)
    return name

#
# Track
#

class Track(object):
    def __init__(self, fn, mtime, artist, album, track, title, **extra_props):
        self.fn = fn

        self.mtime = mtime
        self.artist = artist
        self.album = album
        self.track = track
        self.title = title

        self.artist_url = _clean_url(self.artist)
        self.album_url = _clean_url(self.album)
        self.title_url = _clean_url(self.title)

        self.__dict__.update(extra_props)

    def __repr__(self):
        return "{0}/{1}/{2}-{3}.mp3".format(self.artist_url, self.album_url, self.track, self.title_url)

    @staticmethod
    def from_file(fn, **extra_props):
        t = mutagen.mp3.MP3(os.path.abspath(fn))

        artist = t.has_key('TPE1') and t['TPE1'].text[0] or None
        album  = t.has_key('TALB') and t['TALB'].text[0] or None
        track  = t.has_key('TRCK') and t['TRCK'].text[0] or None
        title  = t.has_key('TIT2') and t['TIT2'].text[0] or None

        assert artist is not None, u'No artist'
        assert album is not None, u'No album'
        assert track is not None, u'No track'
        assert title is not None, u'No title'

        if not artist: raise Exception('No artist')
        if not album: raise Exception('No album')
        if not track: raise Exception('No track')
        if not title: raise Exception('No title')

        if 0:
            for phrase in ['vs.', 'vs', 'ft.', 'ft', 'Meets', 'Presents']:
                artist = artist.replace(' ' + phrase + ' ', ' & ')

        track = track.split('/')[0] if '/' in track else track
        track = int(track)
        track = '{0:02d}'.format(track)

        mtime = os.stat(fn).st_mtime
        mtime = int(mtime)

        return Track(fn, mtime, artist, album, track, title, **extra_props)

    @staticmethod
    def try_from_file(fn, **extra_props):
        try:
            result = Track.from_file(fn, **extra_props)
            print result
            return result
        except Exception as e:
            print fn, ':', str(e)
            return None

    @staticmethod
    def from_obj(t):
        return Track(fn=t['fn'], mtime=t['mtime'], artist=t['artist'], album=t['album'], track=t['track'], title=t['title'])

    def obj(self):
        return dict(fn=self.fn 
            , mtime=self.mtime 
            , artist=self.artist
            , album=self.album
            , track=self.track
            , title=self.title
            )

#
# TrackList
#

def _index_dict(attr_name, list=list):
    @property
    def getter(self):
        attr_idx_name = attr_name + '_idx'
        if hasattr(self, attr_idx_name):
            attr_idx = getattr(self, attr_idx_name)
        else:
            attr_idx = groupby(self.items, lambda track: getattr(track, attr_name))
            attr_idx = { name: list(tracks) for (name, tracks) in attr_idx }
            setattr(self, attr_idx_name, attr_idx)
        return attr_idx
    return getter

def _tracklist_index_dict(attr_name):
    return _index_dict(attr_name, list=lambda items: TrackList(items))

class TrackList(object):
    fn          = _tracklist_index_dict('fn')
    library     = _tracklist_index_dict('library')
    library_url = _tracklist_index_dict('library_url')
    artist      = _tracklist_index_dict('artist')
    artist_url  = _tracklist_index_dict('artist_url')
    album       = _tracklist_index_dict('album')
    album_url   = _tracklist_index_dict('album_url')

    def __init__(self, items=None):
        items = [] if items is None else items
        items = [ t for t in items if t ]
        self.items = items

    def __getitem__(self, i):
        return self.items[i]

    def __unicode__(self):
        return u'[{0}]'.format(', '.join(repr(t) for t in self.items))

#
# Collection
#

class Collection(TrackList):
    def __init__(self, path, files_generator, **extra_props):
        self.path = path

        self.name = os.path.basename(self.path)
        self.name_url = _clean_url(self.name)

        self.__dict__.update(extra_props)

        super(Collection, self).__init__(files_generator(self))

    def find_mp3s(self):
        return [ os.path.relpath(fn.decode('utf8'), self.path) for fn in core.sh.findf('.', '*.mp3') ]

    @staticmethod
    def scan(path):
        curdir = os.getcwd()
        try:
            os.chdir(path)
            files_gen = lambda self: (Track.try_from_file(fn, collection=self.name, collection_url=self.name_url) for fn in self.find_mp3s())
            return Collection(path, files_gen)
        finally:
            os.chdir(curdir)

    def obj(self):
        return { 'path': self.path, 'tracks': [ t.obj() for t in self.items ] }

    @staticmethod
    def from_obj(obj, **x):
        result = Collection(obj['path'], lambda self: (Track.from_obj(track) for track in obj['tracks']))
        result.__dict__.update(x)
        return result

#
# Library 
#

class Library(object):
    name     = _index_dict('name', list=lambda x: list(x)[0])
    name_url = _index_dict('name_url', list=lambda x: list(x)[0])
    path     = _index_dict('path', list=lambda x: list(x)[0])

    def __init__(self, items=None):
        self.items = items or []

    def obj(self):
        return { 
            'items': { 
                c.name_url + '.json': { 'name': c.name, 'path': c.path } 
                for c in self.items } 
        }

    @staticmethod
    def from_obj(obj):
        def collection_gen():
            for fn, collection in obj['items'].items():
                print fn, collection
                if os.path.exists(fn):
                    coll_obj = load_json(fn)
                    yield Collection.from_obj(coll_obj)
                else:
                    yield Collection.scan(collection['path'])
        return Library(list(collection_gen()))

    def save(self, fn):
        for coll in self.items:
            coll_fn = coll.name_url + '.json'
            save_json(coll_fn, coll.obj())
        save_json(fn, self.obj())

    @staticmethod
    def load(fn):
        if os.path.exists(fn):
            obj = load_json(fn)
            return Library.from_obj(obj)
        else:
            return Library()

    def add(self, path):
        self.items.append(Collection.scan(path))

#
# json helper functions
#

obj_to_json = lambda o: json.dumps(o, sort_keys=True, indent=4, encoding='utf8')
json_to_obj = lambda s: json.loads(s, encoding='utf8')

def load_json(fn):
    with open(fn, 'r') as f:
        return json_to_obj(f.read())

def save_json(fn, obj):
    with open(fn, 'w') as f:
        f.write(obj_to_json(obj))
        f.write('\n')

if __name__ == '__main__':
    os.chdir('run')
    L = Library.load('library.json')
    os.chdir('..')
    for p in [
        '/home/joost/shared/Music/Dub & Reggae',
        '/home/joost/shared/Music/Dubstep',
        '/home/joost/shared/Music/Electronic',
        '/home/joost/shared/Music/Exotic',
        '/home/joost/shared/Music/Hip-Hop',
        '/home/joost/shared/Music/Metal & Punk & Surf',
        '/home/joost/shared/Music/Trip-Hop & Turntables',
        '/home/joost/shared/Music/Weird & Pop' ]:
            if not any(c.path == p for c in L.items):
                L.add(p)
    print L.items
    os.chdir('run')
    L.save('library.json')
    os.chdir('..')

    #a1, a2 = 'Orb', 'Adventures Beyond The Ultraworld'
    #b1, b2 = 'orb', 'adventures-beyond-the-ultraworld'

    #a1, a2 = 'Beck', 'Mellow Gold'
    #b1, b2 = 'beck', 'mellow-gold'

    #for t in library.artist[a1]:
        #print unicode(t)

    #print
    #for t in library.artist_url[b1]:
        #print unicode(t)

    #print 
    #for t in library.artist[a1].album[a2]:
        #print unicode(t)

    #print
    #for t in library.artist_url[b1].album_url[b2]:
        #print unicode(t)

    #print
    #for t in lib:
        #print unicode(t)

    #print obj_to_json(L.to_obj())

