import webob
import webob.dec

import resource 

class Redirector(resource.Resource):
	def __init__(self, target):
		self.target = target
	def GET(self, request):
		raise webob.exc.HTTPFound(location=self.target)
