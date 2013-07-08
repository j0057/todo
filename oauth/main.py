import os
import re
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
load_keys('LINKEDIN')

#
# utility functions
#

def print_exchange(r):
    print
    print '>', r.request.method, r.request.url
    for k in sorted(k.title() for k in r.request.headers.keys()):
        print '>', k.title(), ':', r.request.headers[k] 
    print '>'
    print '>', r.request.body
    print
    print '<', r.status_code, r.reason
    for k in sorted(k.title() for k in r.headers.keys()):
        print '<', k.title(), ':', r.headers[k]
    print '<'
    for line in re.split(r'[\r\n]+', r.text):
        print '<', line
    print

def split_mime_header(header_val):
    parts = re.split(r';\s*', header_val)
    value = parts[0]
    attrs = dict(attr.split('=', 1) for attr in parts[1:])
    return value, attrs

#
# OauthInit
#

class OauthInit(xhttp.Resource):
    def __init__(self, key_fmt, client_id, client_secret, authorize_uri, callback_uri):
        super(OauthInit, self).__init__()
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

class GithubInit(OauthInit):
    def __init__(self):
        super(GithubInit, self).__init__('github_{0}', GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
                                         'https://github.com/login/oauth/authorize',
                                         'https://dev.j0057.nl/oauth/github/code/')

class FacebookInit(OauthInit):
    def __init__(self):
        super(FacebookInit, self).__init__('facebook_{0}', FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
                                           'https://www.facebook.com/dialog/oauth',
                                           'https://dev.j0057.nl/oauth/facebook/code/')

class LiveInit(OauthInit):
    def __init__(self):
        super(LiveInit, self).__init__('live_{0}', LIVE_CLIENT_ID, LIVE_CLIENT_SECRET,
                                       'https://login.live.com/oauth20_authorize.srf',
                                       'https://dev.j0057.nl/oauth/live/code/')

class GoogleInit(OauthInit):
    def __init__(self):
        super(GoogleInit, self).__init__('google_{0}', GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                                         'https://accounts.google.com/o/oauth2/auth',
                                         'https://dev.j0057.nl/oauth/google/code/')

    def get_scope(self, request):
        scopes = request['x-get']['scope'] or ''
        return ' '.join(scope if scope in ['openid', 'email'] else 'https://www.googleapis.com/auth/' + scope
                        for scope in scopes.split())

class DropboxInit(OauthInit):
    def __init__(self):
        super(DropboxInit, self).__init__('dropbox_{0}', DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET,
                                          'https://www.dropbox.com/1/oauth2/authorize',
                                          'https://dev.j0057.nl/oauth/dropbox/code/')

class LinkedinInit(OauthInit):
    def __init__(self):
        super(LinkedinInit, self).__init__('linkedin_{0}', LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET,
                                           'https://www.linkedin.com/uas/oauth2/authorization',
                                           'https://dev.j0057.nl/oauth/linkedin/code/')

#
# OauthCode
#

class OauthCode(xhttp.Resource):
    def __init__(self, key_fmt, client_id, client_secret, token_uri, callback_uri, redirect_uri):
        super(OauthCode, self).__init__()
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
                'accept': 'application/json, application/x-www-form-urlencoded;q=0.9, text/plain;q=0.1',
                'content-type': 'application/x-www-form-urlencoded' })

        if r.status_code != 200:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': r.text.encode('utf8') })

        print_exchange(r)

        content_type, _ = split_mime_header(r.headers['content-type'])
        if content_type == 'application/json':
            data = r.json()
            return data['access_token']
        elif content_type == 'application/x-www-form-urlencoded' or content_type == 'text/plain':
            data = urlparse.parse_qs(r.content)
            return data['access_token'][0]
        else:
            raise xhttp.HTTPException(xhttp.status.NOT_IMPLEMENTED, { 
                'x-detail': "Don't know how to handle content type {0}".format(content_type) })

    @xhttp.get({ 'code': r'^.+$', 'state': r'^[-_0-9a-zA-Z]+$',
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

class GithubCode(OauthCode):
    def __init__(self):
        super(GithubCode, self).__init__('github_{0}', GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
                                         'https://github.com/login/oauth/access_token',
                                         'https://dev.j0057.nl/oauth/github/code/',
                                         'https://dev.j0057.nl/oauth/index.xhtml')

class FacebookCode(OauthCode):
    def __init__(self):
        super(FacebookCode, self).__init__('facebook_{0}', FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET,
                                           'https://graph.facebook.com/oauth/access_token',
                                           'https://dev.j0057.nl/oauth/facebook/code/',
                                           'https://dev.j0057.nl/oauth/index.xhtml')

class LiveCode(OauthCode):
    def __init__(self):
        super(LiveCode, self).__init__('live_{0}', LIVE_CLIENT_ID, LIVE_CLIENT_SECRET,
                                       'https://login.live.com/oauth20_token.srf',
                                       'https://dev.j0057.nl/oauth/live/code/',
                                       'https://dev.j0057.nl/oauth/index.xhtml')
                                           
class GoogleCode(OauthCode):
    def __init__(self):
        super(GoogleCode, self).__init__('google_{0}', GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                                         'https://accounts.google.com/o/oauth2/token',
                                         'https://dev.j0057.nl/oauth/google/code/',
                                         'https://dev.j0057.nl/oauth/index.xhtml')

class DropboxCode(OauthCode):
    def __init__(self):
        super(DropboxCode, self).__init__('dropbox_{0}', DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET,
                                           'https://api.dropbox.com/1/oauth2/token',
                                           'https://dev.j0057.nl/oauth/dropbox/code/',
                                           'https://dev.j0057.nl/oauth/index.xhtml')

class LinkedinCode(OauthCode):
    def __init__(self):
        super(LinkedinCode, self).__init__('linkedin_{0}', LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET,
                                           'https://www.linkedin.com/uas/oauth2/accessToken',
                                           'https://dev.j0057.nl/oauth/linkedin/code/',
                                           'https://dev.j0057.nl/oauth/index.xhtml')
                                           
#
# OauthApi
#

class OauthApi(xhttp.Resource):
    def __init__(self, key_fmt, base_uri, access_token='access_token'):
        super(OauthApi, self).__init__()
        self.key_fmt = key_fmt
        self.base_uri = base_uri
        self.access_token = access_token

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request, path):
        path = self.base_uri + path
        params = { k: v[0] for (k, v) in urlparse.parse_qs(request['x-query-string']).items() }
        params.update({ self.access_token: request['x-session'].get(self.key_fmt.format('token'), '') })
        response = requests.get(path, params=params, headers={ 'accept': 'application/json' })
        print_exchange(response)
        return {
            'x-status': response.status_code,
            'content-type': response.headers['content-type'],
            'x-content': response.content }

class GithubApi(OauthApi):
    def __init__(self):
        super(GithubApi, self).__init__('github_{0}', 'https://api.github.com/')

class FacebookApi(OauthApi):
    def __init__(self):
        super(FacebookApi, self).__init__('facebook_{0}', 'https://graph.facebook.com/')

class LiveApi(OauthApi):
    def __init__(self):
        super(LiveApi, self).__init__('live_{0}', 'https://apis.live.net/v5.0/')

class GoogleApi(OauthApi):
    def __init__(self):
        super(GoogleApi, self).__init__('google_{0}', 'https://www.googleapis.com/')

class DropboxApi(OauthApi):
    def __init__(self):
        super(DropboxApi, self).__init__('dropbox_{0}', 'https://api.dropbox.com/')
        
    def GET(self, request, path): # FIXME: path gets unquoted by xhttp ... 
        path = '/'.join(urllib.quote(part) for part in path.split('/'))
        return super(DropboxApi, self).GET(request, path)
        
class DropboxContentApi(OauthApi):
    def __init__(self):
        super(DropboxContentApi, self).__init__('dropbox_{0}', 'https://api-content.dropbox.com/')

class LinkedinApi(OauthApi):
    def __init__(self):
        super(LinkedinApi, self).__init__('linkedin_{0}', 'https://api.linkedin.com/', 'oauth2_access_token')

#
# Sessions
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
# Router
#

class OauthRouter(xhttp.Router):
    def __init__(self):
        super(OauthRouter, self).__init__(
            (r'^/$',                            xhttp.Redirector('/oauth/')),
            (r'^/oauth/$',                      xhttp.Redirector('index.xhtml')),
            
            (r'^/oauth/(.*\.xhtml)$',           xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/oauth/(.*\.js)$',              xhttp.FileServer('static', 'application/javascript')),
            
            (r'^/oauth/google/init/$',          GoogleInit()),
            (r'^/oauth/google/code/$',          GoogleCode()),
            (r'^/oauth/google/api/(.*)$',       GoogleApi()),
            
            (r'^/oauth/live/init/$',            LiveInit()),
            (r'^/oauth/live/code/$',            LiveCode()),
            (r'^/oauth/live/api/(.*)$',         LiveApi()),
            
            (r'^/oauth/facebook/init/$',        FacebookInit()),
            (r'^/oauth/facebook/code/$',        FacebookCode()),
            (r'^/oauth/facebook/api/(.*)$',     FacebookApi()),
            
            (r'^/oauth/github/init/$',          GithubInit()),
            (r'^/oauth/github/code/$',          GithubCode()),
            (r'^/oauth/github/api/(.*)$',       GithubApi()),

            (r'^/oauth/dropbox/init/$',         DropboxInit()),
            (r'^/oauth/dropbox/code/$',         DropboxCode()),
            (r'^/oauth/dropbox/api/(.*)$',      DropboxApi()),
            (r'^/oauth/dropbox/content/(.*)$',  DropboxContentApi()),
            (r'^/oauth/dropbox/(.*\.gif)$',     xhttp.FileServer('static/dropbox/16x16', 'image/gif')),
            
            (r'^/oauth/linkedin/init/$',        LinkedinInit()),
            (r'^/oauth/linkedin/code/$',        LinkedinCode()),
            (r'^/oauth/linkedin/api/(.*)$',     LinkedinApi()),
            
            (r'^/oauth/session/start/$',        SessionStart()),
            (r'^/oauth/session/delete/$',       SessionDelete()),
            (r'^/oauth/session/check/$',        SessionCheck())
        )

app = OauthRouter()
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app)
