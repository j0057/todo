import webob
import webob.exc

import basedec

def debug(request, message):
    if not message.endswith('\n'):
        message += '\n'
    request.environ['wsgi.errors'].write(message)

class partial(basedec.BaseDecorator):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *a, **k):
        result = self.func(request, *a, **k)
        result.accept_ranges = 'bytes'

        size = result.content_length

        if request.range:
            debug(request, 'Range: {0}/{1} {2}'.format(`request.range`, `result.content_length`, `dir(request.range)`))
        else:
            debug(request, 'Range: None')
        if request.range: # and len(request.range.ranges) == 1:
            start, stop = request.range.start, request.range.end
            if stop is None:
                stop = size
            result.status_int = 206
            result.content_range = (start, stop, size)
            result.body_stream.seek(start)
            result.body = result.body_stream.read(stop - start)
        else:
            result.body = result.body_stream.read()
    
        return result

                
