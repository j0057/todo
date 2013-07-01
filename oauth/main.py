import os
import uuid
import urlparse
import urllib

import requests

from jjm import xhttp

#
# session store: a dict
#

SESSIONS = {}

#
# keys come from configuration/environment
#

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')

FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID', '')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET', '')

LIVE_CLIENT_ID = os.environ.get('LIVE_CLIENT_ID', '')
LIVE_CLIENT_SECRET = os.environ.get('LIVE_CLIENT_SECRET', '')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID, '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

print 'GITHUB_CLIENT_ID = {0!r}'.format(GITHUB_CLIENT_ID)
print 'GITHUB_CLIENT_SECRET = {0!r}'.format(GITHUB_CLIENT_SECRET)

print 'FACEBOOK_CLIENT_ID = {0!r}'.format(FACEBOOK_CLIENT_ID)
print 'FACEBOOK_CLIENT_SECRET = {0!r}'.format(FACEBOOK_CLIENT_SECRET)

print 'LIVE_CLIENT_ID = {0!r}'.format(LIVE_CLIENT_ID)
print 'LIVE_CLIENT_SECRET = {0!r}'.format(LIVE_CLIENT_SECRET)

print 'GOOGLE_CLIENT_ID = {0!r}'.format(GOOGLE_CLIENT_ID)
print 'GOOGLE_CLIENT_SECRET = {0!r}'.format(GOOGLE_CLIENT_SECRET)

def session(cookie_key, sessions):
    class session(xhttp.decorator):
        def __call__(self, request, *a, **k):
            if 'x-cookie' in request and cookie_key in request['x-cookie']:
                session_id = request['x-cookie'][cookie_key]
                if session_id in sessions:
                    request['x-session'] = sessions[session_id]
                    return self.func(request, *a, **k)
            request['x-session'] = None
            return self.func(request, *a, **k)
    return session

xhttp.session = session

#
# Authorize
#

class OauthAuthorize(xhttp.Resource):
    def __init__(self, key_fmt, client_id, client_secret, authorize_uri, callback_uri, scope=''):
        super(OauthAuthorize, self).__init__()
        self.key_fmt = key_fmt 
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_uri = authorize_uri
        self.callback_uri = callback_uri
        self.scope = scope

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request):
        request['x-session'][self.key_fmt.format('nonce')] = nonce = str(uuid.uuid4())
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': self.authorize_uri + '?' + urllib.urlencode({
                'client_id': self.client_id,
                'redirect_uri': self.callback_uri,
                'scope': self.scope,
                'state': nonce,
                'response_type': 'code' })
        }

class GithubAuthorize(OauthAuthorize):
    def __init__(self):
        super(GithubAuthorize, self).__init__('github_{0}', GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
                                              'https://github.com/login/oauth/authorize',
                                              'http://dev.j0057.nl/oauth/github/callback/')

class FacebookAuthorize(OauthAuthorize):
    def __init__(self):
        super(FacebookAuthorize, self).__init__('facebook_{0}', 
                                                FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
                                                'https://www.facebook.com/dialog/oauth',
                                                'http://dev.j0057.nl/oauth/facebook/callback/')

class LiveAuthorize(OauthAuthorize):
    def __init__(self):
        super(LiveAuthorize, self).__init__('live_{0}', LIVE_CLIENT_ID, LIVE_CLIENT_SECRET,
                                            'https://login.live.com/oauth20_authorize.srf',
                                            'http://dev.j0057.nl/oauth/live/callback/',
                                            'wl.signin wl.basic wl.skydrive')

class GoogleAuthorize(OauthAuthorize):
    def __init__(self):
        super(GoogleAuthorize, self).__init__('google_{0}', GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                                              'https://accounts.google.com/o/oauth2/auth',
                                              'http://dev.j0057.nl/oauth/google/callback/',
                                              'openid email')

#
# Callback
#

class OauthCallback(xhttp.Resource):
    def __init__(self, key_fmt, client_id, client_secret, token_uri, callback_uri, redirect_uri):
        super(OauthCallback, self).__init__()
        self.key_fmt = key_fmt 
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_uri = token_uri
        self.callback_uri = callback_uri
        self.redirect_uri = redirect_uri

    def get_token(self, code):
        r = requests.post(
            self.token_uri,
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.callback_uri,
                'code': code,
                'grant_type': 'authorization_code' },
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded' })
        if r.status_code != 200:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': r.text.encode('utf8') })
        data = r.json()
        return data['access_token']

    @xhttp.get({ 'code': r'^([-_0-9a-zA-Z]+)$', 'state': r'^[-0-9a-f]+$' })
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request):
        if request['x-get']['state'] != request['x-session'].pop(self.key_fmt.format('nonce')):
            raise xhttp.HTTPException(xhttp.BAD_REQUEST, { 'x-detail': 'Bad state {0}'.format(state) })
        request['x-session'][self.key_fmt.format('token')] = self.get_token(request['x-get']['code'])
        return { 
            'x-status': xhttp.status.SEE_OTHER,
            'location': self.redirect_uri
        }

class GithubCallback(OauthCallback):
    def __init__(self):
        super(GithubCallback, self).__init__('github_{0}', GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
                                             'https://github.com/login/oauth/access_token',
                                             'http://dev.j0057.nl/oauth/github/callback/',
                                             'http://dev.j0057.nl/oauth/index.xhtml')

class FacebookCallback(OauthCallback):
    def __init__(self):
        super(FacebookCallback, self).__init__('facebook_{0}',
                                               FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
                                               'https://graph.facebook.com/oauth/access_token',
                                               'http://dev.j0057.nl/oauth/facebook/callback/',
                                               'http://dev.j0057.nl/oauth/index.xhtml')

    def get_token(self, code): # facebook returns x-www-form-urlencoded instead of json...
        r = requests.post(
            'https://graph.facebook.com/oauth/access_token',
            params={
                'client_id': FACEBOOK_CLIENT_ID,
                'client_secret': FACEBOOK_CLIENT_SECRET,
                'redirect_uri': 'http://dev.j0057.nl/oauth/facebook/callback/',
                'code': code },
            headers={ 'accept': 'application/json' })
        data = urlparse.parse_qs(r.content)
        return data['access_token'][0]

class LiveCallback(OauthCallback):
    def __init__(self):
        super(LiveCallback, self).__init__('live_{0}', LIVE_CLIENT_ID, LIVE_CLIENT_SECRET,
                                           'https://login.live.com/oauth20_token.srf',
                                           'http://dev.j0057.nl/oauth/live/callback/',
                                           'http://dev.j0057.nl/oauth/index.xhtml')
                                           
class GoogleCallback(OauthCallback):
    def __init__(self):
        super(GoogleCallback, self).__init__('google_{0}', GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                                             'https://accounts.google.com/o/oauth2/token',
                                             'http://dev.j0057.nl/oauth/google/callback/',
                                             'http://dev.j0057.nl/oauth/index.xhtml')

#
# Request
#

class OauthRequest(xhttp.Resource):
    def __init__(self, key_fmt, base_uri):
        super(OauthRequest, self).__init__()
        self.key_fmt = key_fmt
        self.base_uri = base_uri

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request, path):
        path = self.base_uri + path
        params = { k: v[0] for (k, v) in urlparse.parse_qs(request['x-query-string']).items() }
        params.update({ 'access_token': request['x-session'].get(self.key_fmt.format('token'), '') })
        response = requests.get( path, params=params, headers={ 'accept': 'application/json' })
        return {
            'x-status': response.status_code,
            'content-type': response.headers['content-type'],
            'x-content': response.content }

class GithubRequest(OauthRequest):
    def __init__(self):
        super(GithubRequest, self).__init__('github_{0}', 'https://api.github.com/')

class FacebookRequest(OauthRequest):
    def __init__(self):
        super(FacebookRequest, self).__init__('facebook_{0}', 'https://graph.facebook.com/')

class LiveRequest(OauthRequest):
    def __init__(self):
        super(LiveRequest, self).__init__('live_{0}', 'https://apis.live.net/v5.0/')

class GoogleRequest(OauthRequest):
    def __init__(self):
        super(GoogleRequest, self).__init('google_{0}', 'https://www.googleapis.com/')

#
# /oauth/session/
#

class SessionStart(xhttp.Resource):
    def GET(self, request):
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {}
        print SESSIONS
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml',
            'set-cookie': 'session_id={0}; Path=/oauth/'.format(session_id)
        }

class SessionDelete(xhttp.Resource):
    @xhttp.cookie({ 'session_id?': '^(.+)$' })
    def GET(self, request):
        session_id = request['x-cookie'].get('session_id', '')
        if session_id and session_id in SESSIONS:
            del SESSIONS[request['x-cookie']['session_id']]
        print SESSIONS
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml',
            'set-cookie': 'session_id=; Path=/oauth/; Expires=Sat, 01 Jan 2000 00:00:00 GMT'
        }

class SessionCheck(xhttp.Resource):
    @xhttp.cookie({ 'session_id?': '^(.+)$' })
    def GET(self, request):
        session_id = request['x-cookie'].get('session_id', None)
        if session_id and session_id not in SESSIONS:
            print '## Session not found, unsetting'
            return {
                'x-status': xhttp.status.NO_CONTENT,
                'set-cookie': 'session_id=; Path=/oauth/; Expires=Sat, 01 Jan 2000 00:00:00 GMT'
            }
        else:
            print '## Session OK: {0!r}'.format(session_id)
            return {
                'x-status': xhttp.status.NO_CONTENT
            }

#
# /
#

class OauthRouter(xhttp.Router):
    def __init__(self):
        super(OauthRouter, self).__init__(
            (r'^/$',                            xhttp.Redirector('/oauth')),
            
            # static stuff
            (r'^/oauth/$',                      xhttp.Redirector('index.xhtml')),
            (r'^/oauth/(.*\.xhtml)$',           xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/oauth/(.*\.js)$',              xhttp.FileServer('static', 'application/javascript')),
            
            # google
            (r'^/oauth/google/authorize/$',     GoogleAuthorize()),
            (r'^/oauth/google/callback/$',      GoogleCallback()),
            (r'^/oauth/google/request/(.*)$',   GoogleRequest()),
            
            # live
            (r'^/oauth/live/authorize/$',       LiveAuthorize()),
            (r'^/oauth/live/callback/$',        LiveCallback()),
            (r'^/oauth/live/request/(.*)$',     LiveRequest()),
            
            # facebook
            (r'^/oauth/facebook/authorize/$',   FacebookAuthorize()),
            (r'^/oauth/facebook/callback/$',    FacebookCallback()),
            (r'^/oauth/facebook/request/(.*)$', FacebookRequest()),
            
            # github
            (r'^/oauth/github/authorize/$',     GithubAuthorize()),
            (r'^/oauth/github/callback/$',      GithubCallback()),
            (r'^/oauth/github/request/(.*)$',   GithubRequest()),
            
            # sessions
            (r'^/oauth/session/start/$',        SessionStart()),
            (r'^/oauth/session/delete/$',       SessionDelete()),
            (r'^/oauth/session/check/$',        SessionCheck())
        )

app = OauthRouter()
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app)
