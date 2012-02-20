import re

import webob
import webob.dec

def url_decode(string):
    string = string.replace('+', '%20')
    return ''.join([ ch if len(ch) == 1 else chr(int(ch[1:], 16))
                     for ch 
                     in re.findall('%..|.', string) ]).decode('utf8')
class Router(object):
    def find(self, path):
        for (pattern, handler) in self.dispatch:
            match = re.match(pattern, path)
            if match:
                return (handler, [ url_decode(arg) for arg in match.groups() ])
        return (None, None)


    @webob.dec.wsgify
    def __call__(self, request):
        path = request.environ['REQUEST_URI'].split('?')[0]

        # try to find the callable that will handle the request
        handler, args = self.find(path)
        if handler:
            return handler(request, *args)

        # not found; try to find it with a / appended
        elif not path.endswith('/'):
            handler, args = self.find(path + '/')
            if handler:
                if request.method in ['GET', 'HEAD']:
                    location = '{0}/{1}{2}'.format(path, '?' if request.query_string else '', request.query_string)
                    return webob.Response(status_int=302, content_type='text/plain', location=location,
                                          body='302 Found\n\n{0} ({1} {2}) --> {3}'.format(self.__class__.__name__, 
                                                                                           request.method, 
                                                                                           repr(request.path), 
                                                                                           location))
                elif request.method in ['POST', 'PUT', 'DELETE']:
                    return handler(request, *args)

        # not found
        return webob.Response(
            status_int=404,
            content_type='text/plain', 
            body='404 Not Found\n\n{0} ({1} {2})'.format(
                type(self).__name__,
                request.method,
                request.path))

