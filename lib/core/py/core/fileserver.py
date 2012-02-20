import datetime
import hashlib
import os
import os.path
import time

import pytz

import webob

import resource 

def serve_stream(request, content_type, stream, last_mod=None, etag=None):
    if last_mod:
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime, tz=pytz.UTC).replace(microsecond=0)
        if request.if_modified_since and request.if_modified_since >= mtime:
            return webob.exc.HTTPNotModified()
        else:
            return webob.Response(content_type=content_type, body=stream.read(), last_modified=last_mod,
                cache_control='Must-revalidate')
    elif etag:
        if request.etag == etag:
            return webob.exc.HTTPNotModified()
        else:
            return webob.Response(content_type=content_type, content_length=stat.st_size, body=data, etag=etag)
    else:
        return webob.Response(content_type=content_type, body=f.read())
        
def serve_file(request, content_type, filename, cache_last_mod=True, cache_etag=False):
	if '/../' in filename:
		raise webob.exc.HTTPForbidden('Suspicious filename')
	
	try:
		stat = os.stat(filename)
	except OSError as e:
		return webob.exc.HTTPNotFound('File not found: {0}'.format(filename))

	if cache_last_mod:
		mtime = datetime.datetime.fromtimestamp(stat.st_mtime, tz=pytz.UTC).replace(microsecond=0)
		if request.if_modified_since and request.if_modified_since >= mtime:
			raise webob.exc.HTTPNotModified()
		else:
			with open(filename, 'rb') as f:
				return webob.Response(content_type=content_type, body=f.read(), content_length=stat.st_size,
					last_modified=stat.st_mtime, accept_ranges='bytes', cache_control='must-revalidate')		
	
	if cache_etag:
		with open(filename, 'rb') as f:
			data = f.read()
			etag = hashlib.sha256(data).hexdigest()
			if request.etag == etag:
				return webob.exc.HTTPNotModified()
			else:
				return webob.Response(content_type=content_type, content_length=stat.st_size, body=data, etag=etag)

	with open(filename, 'rb') as f:
		return webob.Response(content_type=content_type, body=f.read())

class FileServer(resource.Resource):
    def __init__(self, path, content_type):
        self.content_type = content_type
        self.path = path

    def GET(self, request, filename):
		path = '{0}{1}/{2}'.format(request.environ['DOCUMENT_ROOT'], self.path, filename)
		return serve_file(request, self.content_type, path)
