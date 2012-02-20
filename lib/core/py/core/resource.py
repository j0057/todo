import webob.exc

class Resource(object):
    @webob.dec.wsgify
    def __call__(self, request, *args):
        if hasattr(self, request.method):
            return getattr(self, request.method)(request, *args)
        else:
            return webob.Response(status_int=405, content_type='text/plain',
                body='405 Method Not Allowed\n\n{0} ({1} {2})'.format(self.__class__.__name__,
                    request.method, repr(request.path)))
