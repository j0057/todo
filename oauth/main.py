import json
import os
import re
import urllib

try:
    import urlparse as urlparse
except ImportError:
    import urllib.parse as urlparse

import requests

import xhttp

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

def load_keys():
    keys_json_filename = os.environ.get('OAUTH_KEYS', 'keys.json')
    with open(keys_json_filename, 'r') as keys_json:
        keys = json.load(keys_json)
        globals().update(keys)

load_keys()

#
# utility functions
#

def print_exchange(r):
    print()
    print('>', r.request.method, r.request.url)
    for k in sorted(k.title() for k in r.request.headers.keys()):
        print('>', k.title(), ':', r.request.headers[k])
    print('>')
    print('>', r.request.body)
    print()
    print('<', r.status_code, r.reason)
    for k in sorted(k.title() for k in r.headers.keys()):
        print('<', k.title(), ':', r.headers[k])
    print('<')
    for line in re.split(r'[\r\n]+', r.text):
        print('<', line)
    print()

def split_mime_header(header_val):
    parts = re.split(r';\s*', header_val)
    value = parts[0]
    attrs = dict(attr.split('=', 1) for attr in parts[1:])
    return value, attrs

#
# Class variables
#

class Github(object):
    key_fmt       = 'github_{0}'

    client_id     = GITHUB_CLIENT_ID
    client_secret = GITHUB_CLIENT_SECRET

    authorize_uri = 'https://github.com/login/oauth/authorize'
    token_uri     = 'https://github.com/login/oauth/access_token'
    api_base_uri  = 'https://api.github.com'

    callback_uri  = 'https://dev.j0057.nl/oauth/github/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class Facebook(object):
    key_fmt       = 'facebook_{0}'
    
    client_id     = FACEBOOK_CLIENT_ID
    client_secret = FACEBOOK_CLIENT_SECRET
    
    authorize_uri = 'https://www.facebook.com/dialog/oauth'
    token_uri     = 'https://graph.facebook.com/oauth/access_token'
    api_base_uri  = 'https://graph.facebook.com/'

    callback_uri  = 'https://dev.j0057.nl/oauth/facebook/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'
    
class Live(object):
    key_format    = 'live_{0}'
    
    client_id     = LIVE_CLIENT_ID
    client_secret = LIVE_CLIENT_SECRET
    
    authorize_uri = 'https://login.live.com/oauth20_authorize.srf'
    token_uri     = 'https://login.live.com/oauth20_token.srf'
    api_base_uri  = 'https://apis.live.net/v5.0/'

    callback_uri  = 'https://dev.j0057.nl/oauth/live/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

#
# OauthInit
#

class OauthInit(xhttp.Resource):
    def get_scope(self, request):
        return request['x-get']['scope'] or ''

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    @xhttp.get({ 'scope?': '.+', 'session_id*': '.*' })
    def GET(self, request):
        request['x-session'][self.key_fmt.format('nonce')] = nonce = random()
        authorize_uri = self.authorize_uri + '?' + urllib.urlencode({
            'client_id': self.client_id,
            'redirect_uri': self.callback_uri,
            'scope': self.get_scope(request),
            'state': nonce,
            'response_type': 'code' })
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': authorize_uri }

class GithubInit(OauthInit, Github):
    pass

class FacebookInit(OauthInit, Facebook):
    pass

class LiveInit(OauthInit, Live):
    pass

class GoogleInit(OauthInit):
    key_fmt = 'google_{0}'
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    authorize_uri = 'https://accounts.google.com/o/oauth2/auth'
    callback_uri = 'https://dev.j0057.nl/oauth/google/code/'

    def get_scope(self, request):
        scopes = request['x-get']['scope'] or ''
        return ' '.join(scope if scope in ['openid', 'email'] else 'https://www.googleapis.com/auth/' + scope
                        for scope in scopes.split())

class DropboxInit(OauthInit):
    key_fmt = 'dropbox_{0}'
    client_id = DROPBOX_CLIENT_ID
    client_secret = DROPBOX_CLIENT_SECRET
    authorize_uri = 'https://www.dropbox.com/1/oauth2/authorize'
    callback_uri = 'https://dev.j0057.nl/oauth/dropbox/code/'

class LinkedinInit(OauthInit):
    key_fmt = 'linkedin_{0}'
    client_id = LINKEDIN_CLIENT_ID
    client_secret = LINKEDIN_CLIENT_SECRET
    authorize_uri = 'https://www.linkedin.com/uas/oauth2/authorization'
    callback_uri = 'https://dev.j0057.nl/oauth/linkedin/code/'

class RedditInit(OauthInit):
    key_fmt = 'reddit_{0}'
    client_id = REDDIT_CLIENT_ID
    client_secret = REDDIT_CLIENT_SECRET
    authorize_uri = 'https://ssl.reddit.com/api/v1/authorize'
    callback_uri = 'https://dev.j0057.nl/oauth/reddit/code/'

class J0057TodoInit(OauthInit):
    key_fmt = 'j0057_todo_{0}'
    client_id = J0057_TODO_CLIENT_ID
    client_secret = J0057_TODO_CLIENT_SECRET
    authorize_uri = 'http://dev2.j0057.nl/todo/authorize/'
    callback_uri = 'https://dev.j0057.nl/oauth/j0057-todo/code/'

#
# OauthCode
#

class OauthCode(xhttp.Resource):
    def get_form(self, code):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.callback_uri,
            'code': code,
            'grant_type': 'authorization_code' }

    def get_headers(self):
        headers = {
            'accept': 'application/json, application/x-www-form-urlencoded;q=0.9, text/plain;q=0.1',
            'content-type': 'application/x-www-form-urlencoded' }
        headers.update(self.get_authorization())
        return headers

    def get_authorization(self):
        return {}

    def get_token(self, code):
        r = requests.post(self.token_uri, data=self.get_form(code), headers=self.get_headers())

        print_exchange(r)

        if r.status_code != 200:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': r.text.encode('utf8') })

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

class GithubCode(OauthCode, Github):
    pass

class FacebookCode(OauthCode, Facebook):
    pass

class LiveCode(OauthCode, Live):
    pass

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
                                           
class RedditCode(OauthCode):
    def __init__(self):
        super(RedditCode, self).__init__('reddit_{0}', REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
                                         'https://ssl.reddit.com/api/v1/access_token',
                                         'https://dev.j0057.nl/oauth/reddit/code/',
                                         'https://dev.j0057.nl/oauth/index.xhtml')

    def get_authorization(self):
        auth = 'Basic ' + '{0}:{1}'.format(self.client_id, self.client_secret).encode('base64')[:-1]
        return { 'authorization': auth }

class J0057TodoCode(OauthCode):
    def __init__(self):
        super(J0057TodoCode, self).__init__('j0057_todo_{0}',
                                            J0057_TODO_CLIENT_ID, J0057_TODO_CLIENT_SECRET,
                                            'http://dev2.j0057.nl/todo/access_token/',
                                            'https://dev.j0057.nl/oauth/j0057-todo/code/',
                                            'https://dev.j0057.nl/oauth/index.xhtml')

#
# OauthApi
#

class OauthApi(xhttp.Resource):
    access_token = None

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request, path):
        token = request['x-session'].get(self.key_fmt.format('token'), '')
        params = { k: v[0] for (k, v) in urlparse.parse_qs(request['x-query-string']).items() }
        headers = { 'accept': 'application/json' }
        if self.access_token:
            params.update({ self.access_token: token })
        else:
            headers.update({ 'authorization': 'Bearer {0}'.format(token) })
        response = requests.get(self.base_uri + path, params=params, headers=headers)
        print_exchange(response)
        return {
            'x-status': response.status_code,
            'content-type': response.headers['content-type'],
            'x-content': response.content }

class GithubApi(OauthApi, Github):
    pass

class FacebookApi(OauthApi, Facebook):
    pass

class LiveApi(OauthApi, Live):
    pass

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

class RedditApi(OauthApi):
    def __init__(self):
        super(RedditApi, self).__init__('reddit_{0}', 'https://oauth.reddit.com/')

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
        if session_id and (session_id not in SESSIONS):
            return {
                'x-status': xhttp.status.OK,
                'x-content': json.dumps({
                    'session': False,
                    'tokens': {}
                }),
                'content-type': 'application/json',
                'set-cookie': 'session_id=; Path=/oauth/; Expires=Sat, 01 Jan 2000 00:00:00 GMT',
            }
        else:
            session = SESSIONS.get(session_id, {})
            return {
                'x-status': xhttp.status.OK,
                'x-content': json.dumps({
                    'session': bool(session),
                    'tokens': {
                        'github': 'github_token' in session,
                        'facebook': 'facebook_token' in session,
                        'live': 'live_token' in session,
                        'google': 'google_token' in session,
                        'dropbox': 'dropbox_token' in session,
                        'linkedin': 'linkedin_token' in session,
                        'reddit': 'reddit_token' in session,
                    }
                }),
                'content-type': 'application/json'
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
            
            (r'^/oauth/reddit/init/$',          RedditInit()),
            (r'^/oauth/reddit/code/$',          RedditCode()),
            (r'^/oauth/reddit/api/(.*)$',       RedditApi()),

            (r'^/oauth/j0057-todo/init/$',      J0057TodoInit()),
            (r'^/oauth/j0057-todo/code/$',      J0057TodoCode()),
            
            (r'^/oauth/session/start/$',        SessionStart()),
            (r'^/oauth/session/delete/$',       SessionDelete()),
            (r'^/oauth/session/check/$',        SessionCheck())
        )

app = OauthRouter()
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app)
