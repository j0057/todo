import uuid

import webob
import webob.dec
import webob.exc

import easydict

sessions = {}

def session_loader(application):
    @webob.dec.wsgify
    def session_loader_app(request):
        global sessions
        request.session = None
        #request.environ['wsgi.errors'].write(repr(request.cookies) + '\n')
        #request.environ['wsgi.errors'].write(repr(sessions) + '\n')
        if 'session' in request.cookies:
            if request.cookies['session'] in sessions:
                request.session = sessions[request.cookies['session']]
        return application(request)
    return session_loader_app

def start_session(request, response):
    global sessions
    # create session
    sessionid = str(uuid.uuid4())
    sessions[sessionid] = easydict.EasyDict()
    # add to request
    request.session = sessions[sessionid]
    # set cookie in response
    response.set_cookie('session', sessionid)

def end_session(request, response):
    global sessions
    # destroy session
    del sessions[request.cookie['sessions']]
    # remove from request
    request.session = None
    # set cookie in response
    response.set_cookie('session', None)

