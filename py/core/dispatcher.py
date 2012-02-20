import re

import webob.dec
import webob.exc

import core.resource

class Dispatcher(object):
	@webob.dec.wsgify
	def __call__(self, request, *args):
		request.charset = 'utf8' # not a good hack !

		# save pathinfo so that we can restore it just before running the controller
		if not hasattr(request, 'full_path_info'):
			request.full_path_info = request.path_info
		
		# dispatch request to sub-resource
		segment = request.path_info_peek() or ''
		for (pattern, obj) in self.dispatch:
			match = re.match(pattern, segment)
			if match:
				request.path_info_pop()
				if isinstance(obj, core.Resource) and request.path_info:
					break
				return obj(request, *(args + match.groups()))

		# handle no more path segments left
		if request.path_info == '':
			# add slash if it's a GET request
			if request.method == 'GET':
				raise webob.exc.HTTPFound(add_slash=True)
			# just run the handler if it's POST, PUT or DELETE
			else:
				handler = getattr(self, request.method, None)
				if handler:
					return handler(request, *args)
				else:
					raise webob.exc.HTTPMethodNotAllowed()

		# still some path left, but the right dispatcher is now found
		if request.path_info == '/':
			handler = getattr(self, request.method, None)
			if handler:
				return handler(request, *args)
			else:
				raise webob.exc.HTTPMethodNotAllowed()

		# no handler could be found, return a 404
		raise webob.exc.HTTPNotFound(
			'{0}.{1}: {2} script_name="{3}" path_info="{4}" segment="{5}"'.format(
				self.__class__.__module__,
				self.__class__.__name__,
				request.method,
				request.script_name,
				request.path_info,
				segment))
