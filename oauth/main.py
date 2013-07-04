import os
import urlparse
import urllib

import requests

from jjm import xhttp

#
# session store: a dict
#

SESSIONS = {}

#
# generate something random
#

def random(n=57):
    return os.urandom(n).encode('base64')[:-1].replace('+','_').replace('/','-')

#
# keys come from configuration/environment
#

def load_keys(name):
    client_id     = '{0}_CLIENT_ID'.format(name)
    client_secret = '{0}_CLIENT_SECRET'.format(name)
    keys = {
        client_id    : os.environ.get(client_id, ''),
        client_secret: os.environ.get(client_secret, '') 
    }
    globals().update(keys)
    print keys
        
load_keys('GITHUB')
load_keys('FACEBOOK')
load_keys('LIVE')
load_keys('GOOGLE')
load_keys('DROPBOX')

#
# Authorize
#

class OauthAuthorize(xhttp.Resource):
    def __init__(self, key_fmt, client_id, client_secret, authorize_uri, callback_uri):
        super(OauthAuthorize, self).__init__()
        self.key_fmt = key_fmt 
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_uri = authorize_uri
        self.callback_uri = callback_uri

    def get_scope(self, request):
        return request['x-get']['scope'] or ''

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    @xhttp.get({ 'scope?': '.+', 'session_id*': '.*' })
    def GET(self, request):
        request['x-session'][self.key_fmt.format('nonce')] = nonce = random()
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': self.authorize_uri + '?' + urllib.urlencode({
                'client_id': self.client_id,
                'redirect_uri': self.callback_uri,
                'scope': self.get_scope(request),
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
                                            'http://dev.j0057.nl/oauth/live/callback/')

class GoogleAuthorize(OauthAuthorize):
    def __init__(self):
        super(GoogleAuthorize, self).__init__('google_{0}', GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                                              'https://accounts.google.com/o/oauth2/auth',
                                              'http://dev.j0057.nl/oauth/google/callback/')

    def get_scope(self, request):
        scopes = request['x-get']['scope'] or ''
        return ' '.join(scope if scope in ['openid', 'email'] else 'https://www.googleapis.com/auth/' + scope
                        for scope in scopes.split())

class DropboxAuthorize(OauthAuthorize):
    def __init__(self):
        super(DropboxAuthorize, self).__init__('dropbox_{0}', DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET,
                                               'https://www.dropbox.com/1/oauth2/authorize',
                                               'https://dev.j0057.nl/oauth/dropbox/callback/')

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

    @xhttp.get({ 'code': r'^.+$', 'state': r'^[-0-9a-f]+$',
                 'authuser?': '.*', 'prompt?': '.*', 'session_state?': '.*' })
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
        super(FacebookCallback, self).__init__('facebook_{0}', FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
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

class DropboxCallback(OauthCallback):
    def __init__(self):
        super(DropboxCallback, self).__init__('dropbox_{0}', DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET,
                                              'https://api.dropbox.com/1/oauth2/token',
                                              'https://dev.j0057.nl/oauth/dropbox/callback/',
                                              'https://dev.j0057.nl/oauth/index.xhtml')

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
        super(GoogleRequest, self).__init__('google_{0}', 'https://www.googleapis.com/')

#
# /oauth/session/
#

class SessionStart(xhttp.Resource):
    def GET(self, request):
        session_id = random()
        SESSIONS[session_id] = {}
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
            del SESSIONS[session_id]
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
            return {
                'x-status': xhttp.status.NO_CONTENT,
                'set-cookie': 'session_id=; Path=/oauth/; Expires=Sat, 01 Jan 2000 00:00:00 GMT'
            }
        else:
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

            # dropbox
            (r'^/oauth/dropbox/authorize/$',    DropboxAuthorize()),
            (r'^/oauth/dropbox/callback/$',     DropboxCallback()),
            
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
