#!/usr/bin/env python2.7

import os
import os.path
import re
import sys
import codecs
import json

from urllib import quote_plus as urlencode

import mutagen
import mutagen.id3
import mutagen.mp3

from .. import sh

mutagen.id3.pedantic = False

stdout = codecs.getwriter('utf8')(sys.stdout)
stderr = codecs.getwriter('utf8')(sys.stderr)

def get_tags(fn):
    stderr.write(os.path.basename(fn) + '\n')
    with open(fn, 'rb') as f:
        try:
            t = mutagen.mp3.MP3(fn)
        except Exception, e:
            stderr.write(u'ERROR: {0} - {1}\n'.format(type(e).__name__, e))
            stderr.write(u'       {0}\n'.format(fn))
            return None

        artist  = t.has_key('TPE1') and t['TPE1'].text[0] or None
        album   = t.has_key('TALB') and t['TALB'].text[0] or None
        track   = t.has_key('TRCK') and t['TRCK'].text[0] or None
        name    = t.has_key('TIT2') and t['TIT2'].text[0] or None
        timestamp = os.stat(fn).st_mtime

        try:
            assert artist is not None, u'No artist: ' + fn
            assert album is not None, u'No album: ' + fn
            assert track is not None, u'No track: ' + fn
            assert name is not None, u'No name: ' + fn
        except Exception, e:
            stderr.write(u'ERROR: {0} - {1}\n'.format(type(e).__name__, e))
            stderr.write(u'       {0}'.format(fn))
            return None

        if '/' in track:
            track = track.split('/')[0]
        track = int(track)

        for phrase in ['vs', 'Meets', 'ft.', 'ft', 'Presents']:
            artist = artist.replace(' ' + phrase + ' ', ' & ')

        return (artist, album, track, name, timestamp, fn)

def scan_path(path):
    for filename in sh.findf(path, '*.mp3'):
        yield filename.decode('utf8')

def scan_paths(paths):
    for path in paths:
        stderr.write('# ' + path + '\n')
        for filename in scan_path(path):
            yield filename
           
def gen_json(values):
    result = {}
    for artist, album, track, name, timestamp, fn in values:
        if artist not in result:
            result[artist] = {}
        if album not in result[artist]:
            result[artist][album] = {}
        result[artist][album]['{0:02}'.format(int(track))] = {
            'name':name, 
            'fn':fn,
            't':int(timestamp)
        }
    stderr.write('\nGenerating index... ')
    json.dump(result, stdout, sort_keys=True, indent=2, ensure_ascii=False)
    stderr.write('Done.\n\n')

def load_current(fn):
    try:
        with open(fn) as f:
            mp3 = json.load(codecs.getreader('utf8')(f))
        return (mp3, {
            track_info['fn']: {
                'artist_name': artist_name,
                'album_name': album_name,
                'track_num': track_num,
                'track_name': track_info['name'],
                't': track_info['t'],
                'fn': track_info['fn']
            }
            for (artist_name, albums) in mp3.items()
            for (album_name, tracks) in albums.items()
            for (track_num, track_info) in tracks.items() })

    except Exception as e: # no big deal, just create new database
        sys.stderr.write('{0}: {1}\n\n'.format(type(e).__name__, str(e)))
        return ({}, {})
    
def main(paths):
    current, current_files = load_current('mp3.json')

    filenames = ((fn, int(os.stat(fn).st_mtime)) for fn in scan_paths(paths))

    tags = (get_tags(fn)
        if fn not in current_files or current_files[fn]['t'] != t
        else current_files[fn]
        for (fn, t) in filenames)

    gen_json(tag for tag in tags if tag)


if __name__ == '__main__':
    paths = sys.argv[1:]
    main(paths)

