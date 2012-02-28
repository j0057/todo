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

import sh

mutagen.id3.ID3.PEDANTIC = False

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
        #year    = t.has_key('TDRC') and t['TDRC'].text[0].year or None
        name    = t.has_key('TIT2') and t['TIT2'].text[0] or None
        #comment = t.has_key("COMM::'\\x00\\x00\\x00'") \
        #          and t["COMM::'\\x00\\x00\\x00'"].text[0] \
        #          or None
        timestamp = os.stat(fn).st_mtime

        #label, catno = None, None
        #if comment:
        #    match = re.match(r'(.*) \[(.*)\]', comment)
        #    if match:
        #        label, catno = match.groups()

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

        artist = artist.replace(' vs ', ' & ')
        artist = artist.replace(' Meets ', ' & ')
        artist = artist.replace(' ft. ', ' & ')
        artist = artist.replace(' Presents ', ' & ')

        #eturn (artist, album, track, name, year, timestamp, fn)
        return (artist, album, track, name, timestamp, fn)

def scan_path(path):
    for filename in sh.findf(path, '*.mp3'):
        yield filename.decode('utf8')

def scan_paths(paths):
    for path in paths:
        stderr.write('# ' + path + '\n')
        for filename in scan_path(path):
            yield filename
           
def count(L):
    result = 0
    for _ in L:
        result += 1
    return result
 
def gen_json(values):
    result = {}
    for artist, album, track, name, timestamp, fn in values:
        if artist not in result:
            result[artist] = {}
        if album not in result[artist]:
            #tderr.write(u'\n{0} - {1}'.format(artist, album))
            result[artist][album] = {}
        #tderr.write('.')
        result[artist][album]['{0:02}'.format(int(track))] = {
            'name':name, 
            'fn':fn,
            't':int(timestamp)
        }
    stderr.write('\nGenerating index... ')
    json.dump(result, stdout, sort_keys=True, indent=2, ensure_ascii=False)
    stderr.write('Done.\n\n')

    stderr.write('Artists: {0}\n'.format(count(result)))
    stderr.write('Albums: {0}\n'.format(count(
        album 
        for artist in result
        for album in result[artist])))
    stderr.write('Tracks: {0}\n'.format(count(
        track
        for artist in result
        for album in result[artist]
        for track in result[artist][album])))

def load_current(fn):
    try:
        sys.stderr.write('Reading current {0}... '.format(fn))
        with open(fn) as f:
            mp3 = json.load(codecs.getreader('utf8')(f))
            files = { 
                mp3[ar][al][t]['fn']: 
                    (ar, al, t, mp3[ar][al][t]['name'], mp3[ar][al][t]['t'], mp3[ar][al][t]['fn'])
                for ar in mp3
                for al in mp3[ar]
                for t in mp3[ar][al] }
            sys.stderr.write('Done.\n\n')
            return (mp3, files)
    except Exception as e:
        sys.stderr.write('{0}: {1}\n\n'.format(type(e).__name__, str(e)))
        return ({}, {})
    
def main(paths):
    current, current_files = load_current('web/mp3.json')
    filenames = ((fn, int(os.stat(fn).st_mtime)) for fn in scan_paths(paths))
    tags = (get_tags(fn)
        if fn not in current_files or current_files[fn][4] != t
        else current_files[fn]
        for (fn, t) in filenames)
    #tags = (get_tags(fn) for (fn, t) in filenames)
    gen_json(tag for tag in tags if tag)

#def path_encode(u):
#    result = ''
#    UNRESERVED = map(ord, "-._~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
#    HEX_DIGITS = '0123456789ABCDEF'
#    return ''.join(
#        chr(val) 
#        if val in UNRESERVED 
#        else '%' + HEX_DIGITS[val/16] + HEX_DIGITS[val%16]
#        for val in (ord(cp) for cp in u.encode('utf8')))

#def path_join(*parts):
#    return '/' + '/'.join(path_encode(part) for part in parts)

if __name__ == '__main__':
    paths = sys.argv[1:]
    main(paths)

