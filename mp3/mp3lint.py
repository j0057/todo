#!/usr/bin/python

import codecs
import os
import os.path
import sys
import StringIO

import mutagen
import mutagen.mp3

import pil.Image

import sh

stdout = codecs.getwriter('utf8')(sys.stdout)
stderr = codecs.getwriter('utf8')(sys.stderr)

safe = lambda s: s.replace(':', '_').replace('?', '_').replace('/', '_').replace('*', '-')

def scan_path(path):
	for filename in sh.findf(path, '*.mp3'):
		yield filename.decode('utf8')

def scan_paths(paths):
	for path in paths:
		for filename in scan_path(path):
			yield filename

class Mp3Exception(Exception):
	type = 'exception'
	def __init__(self, checkname, info, filename):
		self.checkname = checkname
		self.filename = filename
		self.info = info
	def __unicode__(self):
		return u'{0}:{1}:{2}:{3}'.format(self.type, self.checkname, self.info, self.filename)

class Mp3Error(Mp3Exception):
	type = 'error'
class Mp3Warning(Mp3Exception):
	type = 'warning'

def check_file(fn):
	try:
		bn = os.path.basename(fn)
		pn = os.path.dirname(fn)
		fnparts = bn.split(' - ', 3)
		
		# check filename format
		if len(fnparts) != 4:
			raise Mp3Error('FilenameLength', len(fnparts), bn)
		
		# check basic ID3 tagging info
		try:
			id3 = mutagen.mp3.MP3(fn)
		except Exception as e:
			raise Mp3Error(type(e).__name__, repr(e), bn)

		#print id3.keys(), 
		id3artist = id3.has_key('TPE1') and id3['TPE1'].text[0] or None
		id3album = id3.has_key('TALB') and id3['TALB'].text[0] or None
		id3track = id3.has_key('TRCK') and id3['TRCK'].text[0] or None
		id3name = id3.has_key('TIT2') and id3['TIT2'].text[0] or None
		id3image = id3.has_key('APIC:') and id3['APIC:'] or None
		id3year = id3.has_key('TDRC') and id3['TDRC'] or None
		if not id3artist: raise Mp3Error('TagMissing', 'artist', bn)
		if not id3album: raise Mp3Error('TagMissing', 'album', bn)
		if not id3track: raise Mp3Error('TagMissing', 'track', bn)
		if not id3name: raise Mp3Error('TagMissing', 'name', bn)
		if not id3year: raise Mp3Error('TagMissing', 'year', bn)

		# check cover exists
		if not id3image:
			raise Mp3Error('NoCover', '', bn)
		
		# check cover is image/jpeg
		if id3image.mime not in ('image/jpg', 'image/jpeg'):
			raise Mp3Error('CoverContentType', id3image.mime, bn)
		
		# check cover file exists
		cf = safe(u'{0} - {1}.jpg'.format(id3artist, id3album))
		if not os.path.exists(u'{0}/{1}'.format(pn, cf).encode('utf8')):
			raise Mp3Error('CoverFileMissing', cf, bn)
		
		# check for pollution
		if os.path.exists(u'{0}/AlbumArtSmall.jpg'.format(pn).encode('utf8')):
			raise Mp3Error('Pollution', 'AlbumArtSmall', bn)
		if os.path.exists(u'{0}/folder.jpg'.format(pn).encode('utf8')):
			raise Mp3Error('Pollution', 'folder.jpg', bn)

		# check dimensions are reasonable
		f = StringIO.StringIO(id3image.data)
		image = pil.Image.open(f)
		w,h = image.size
		if w < 200 or h < 200:
			raise Mp3Warning('CoverSize', '{0}x{1}'.format(w,h), bn)
		
	except Mp3Exception as e:
		stdout.write(unicode(e) + '\n')

if __name__ == '__main__':
	try:
		for filename in scan_paths(sys.argv[1:]):
			check_file(filename)
	except IOError:
		pass
