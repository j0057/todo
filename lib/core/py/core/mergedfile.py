import datetime
import hashlib
import os
import os.path
import time

import pytz

import webob

import resource 

class MergedFile(resource.Resource):
	def __init__(self, path, content_type):
		self.content_type = content_type
		self.path = path
		self.mtime = {}
		self.cache = {}

	def _gen_comment(self, path):
		filename = os.path.basename(path)
		if self.content_type == 'text/javascript':
			return '//\n// {0}\n//\n\n'.format(filename)
		else:
			return ''
		
	def GET(self, request, filenames, ext):
		# be paranoid
		if '/../' in filenames:
			raise webob.exc.HTTPForbidden('Suspicious filename')
	
		# generate full path names
		paths = [ '{0}{1}/{2}.js'.format(request.environ['DOCUMENT_ROOT'], self.path, filename, ext)
			for filename in filenames.split('+') ]
		
		# try find files
		try:
			stats = map(os.stat, paths)
		except OSError as e:
			return webob.exc.HTTPNotFound('Files not found: {0}'.format(repr(paths)))
		
		# check last modification time
		mtime = max(stat.st_mtime for stat in stats)
		if (filenames in self.mtime) and (mtime > self.mtime[filenames]):
			del self.mtime[filenames]
			del self.cache[filenames]
		self.mtime[filenames] = mtime
		
		# check if request is conditional based on Last-Modified
		lastmod = datetime.datetime.fromtimestamp(mtime, tz=pytz.UTC).replace(microsecond=0)
		if request.if_modified_since and request.if_modified_since >= lastmod:
			raise webob.exc.HTTPNotModified()		
		
		# merge files
		if not filenames in self.cache:
			self.cache[filenames] = ''
			for path in paths:
				with open(path, 'rb') as f:
					self.cache[filenames] += self._gen_comment(path)
					self.cache[filenames] += f.read();
					self.cache[filenames] += '\n'
		
		# return the merged file
		return webob.Response(content_type=self.content_type, body=self.cache[filenames],
			last_modified=lastmod, cache_control='must-revalidate')
