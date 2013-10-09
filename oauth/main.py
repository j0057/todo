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
# Class variables
#

class Github(object):
    key_fmt       = 'github_{0}'

    client_id     = GITHUB_CLIENT_ID
    client_secret = GITHUB_CLIENT_SECRET

    authorize_uri = 'https://github.com/login/oauth/authorize'
    token_uri     = 'https://github.com/login/oauth/access_token'
    api_base_uri  = 'https://api.github.com/'

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
    key_fmt       = 'live_{0}'
    
    client_id     = LIVE_CLIENT_ID
    client_secret = LIVE_CLIENT_SECRET
    
    authorize_uri = 'https://login.live.com/oauth20_authorize.srf'
    token_uri     = 'https://login.live.com/oauth20_token.srf'
    api_base_uri  = 'https://apis.live.net/v5.0/'

    callback_uri  = 'https://dev.j0057.nl/oauth/live/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class Google(object):
    key_fmt       = 'google_{0}'

    client_id     = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET

    authorize_uri = 'https://accounts.google.com/o/oauth2/auth'
    token_uri     = 'https://accounts.google.com/o/oauth2/token'
    api_base_uri  = 'https://www.googleapis.com/'

    callback_uri  = 'https://dev.j0057.nl/oauth/google/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class Dropbox(object):
    key_fmt       = 'dropbox_{0}'

    client_id     = DROPBOX_CLIENT_ID
    client_secret = DROPBOX_CLIENT_SECRET

    authorize_uri = 'https://www.dropbox.com/1/oauth2/authorize'
    token_uri     = 'https://api.dropbox.com/1/oauth2/token'
    api_base_uri  = 'https://api.dropbox.com/'

    callback_uri  = 'https://dev.j0057.nl/oauth/dropbox/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class Linkedin(object):
    key_fmt       = 'linkedin_{0}'

    client_id     = LINKEDIN_CLIENT_ID
    client_secret = LINKEDIN_CLIENT_SECRET

    authorize_uri = 'https://www.linkedin.com/uas/oauth2/authorization'
    token_uri     = 'https://www.linkedin.com/uas/oauth2/accessToken'
    api_base_uri  = 'https://api.linkedin.com/'

    callback_uri  = 'https://dev.j0057.nl/oauth/linkedin/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class Reddit(object):
    key_fmt       = 'reddit_{0}'

    client_id     = REDDIT_CLIENT_ID
    client_secret = REDDIT_CLIENT_SECRET

    authorize_uri = 'https://ssl.reddit.com/api/v1/authorize'
    token_uri     = 'https://ssl.reddit.com/api/v1/access_token'
    api_base_uri  = 'https://oauth.reddit.com/'

    callback_uri  = 'https://dev.j0057.nl/oauth/reddit/code/'
    redirect_uri  = 'https://dev.j0057.nl/oauth/index.xhtml'

class J0057Todo(object):
    key_fmt       = 'j0057_todo_{0}'

    client_id     = J0057_TODO_CLIENT_ID
    client_secret = J0057_TODO_CLIENT_SECRET

    authorize_uri = 'http://dev2.j0057.nl/todo/authorize/'
    token_uri     = 'http://dev2.j0057.nl/todo/access_token/'
    api_base_uri  = 'http://dev2.j0057.nl/todo/'

    callback_uri  = 'https://dev.j0057.nl/oauth/j0057-todo/code/'
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

class GoogleInit(OauthInit, Google):
    def get_scope(self, request):
        scopes = request['x-get']['scope'] or ''
        return ' '.join(scope if scope in ['openid', 'email'] else 'https://www.googleapis.com/auth/' + scope
                        for scope in scopes.split())

class DropboxInit(OauthInit, Dropbox):
    pass

class LinkedinInit(OauthInit, Linkedin):
    pass

class RedditInit(OauthInit, Reddit):
    pass

class J0057TodoInit(OauthInit, J0057Todo):
    pass

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

    def parse_token(self, response, content_type):
        if content_type == 'application/json':
            json = response.json()
            return json['access_token']

    def request_token(self, code):
        # post request for getting access token
        response = requests.post(self.token_uri, data=self.get_form(code), headers=self.get_headers())
        print_exchange(response)
        if response.status_code != 200:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': response.text.encode('utf8') })

        # get access code from response
        content_type, _ = split_mime_header(response.headers['content-type'])
        access_token = self.parse_token(response, content_type)
        if not access_token:
            raise xhttp.HTTPException(xhttp.status.NOT_IMPLEMENTED, {
                'x-detail': "Don't know how to handle content type {0}".format(content_type) })
        return access_token

    @xhttp.get({ 'code': r'^.+$', 'state': r'^[-_0-9a-zA-Z]+$',
                 'authuser?': '.*', 'prompt?': '.*', 'session_state?': '.*' })
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request):
        if request['x-get']['state'] != request['x-session'].pop(self.key_fmt.format('nonce')):
            raise xhttp.HTTPException(xhttp.BAD_REQUEST, { 'x-detail': 'Bad state {0}'.format(state) })
        request['x-session'][self.key_fmt.format('token')] = self.request_token(request['x-get']['code'])
        return { 
            'x-status': xhttp.status.SEE_OTHER,
            'location': self.redirect_uri
        }

class GithubCode(OauthCode, Github):
    pass

class FacebookCode(OauthCode, Facebook):
    def parse_token(self, response, content_type):
        if content_type in ['application/x-www-form-urlencoded', 'text/plain']:
            form = urlparse.parse_qs(response.content)
            return form['access_token'][0]
        else:
            return super(FacebookCode, self).parse_token(response, content_type)

class LiveCode(OauthCode, Live):
    pass

class GoogleCode(OauthCode, Google):
    pass

class DropboxCode(OauthCode, Dropbox):
    pass

class LinkedinCode(OauthCode, Linkedin):
    pass
                                           
class RedditCode(OauthCode, Reddit):
    def get_authorization(self):
        auth = 'Basic ' + '{0}:{1}'.format(self.client_id, self.client_secret).encode('base64')[:-1]
        return { 'authorization': auth }

class J0057TodoCode(OauthCode, J0057Todo):
    pass

#
# OauthApi
#

class OauthApi(xhttp.Resource):
    def set_token(self, headers, params, token):
        headers.update({ 'authorization': 'Bearer {0}'.format(token) })

    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.session('session_id', SESSIONS)
    def GET(self, request, path):
        token = request['x-session'].get(self.key_fmt.format('token'), '')
        params = { k: v[0] for (k, v) in urlparse.parse_qs(request['x-query-string']).items() }
        headers = { 'accept': 'application/json' }
        self.set_token(headers, params, token)
        response = requests.get(self.api_base_uri + path, params=params, headers=headers)
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

class GoogleApi(OauthApi, Google):
    pass

class DropboxApi(OauthApi, Dropbox):
    def GET(self, request, path): 
        path = '/'.join(urllib.quote(part) for part in path.split('/'))
        return super(DropboxApi, self).GET(request, path)
        
class DropboxContentApi(OauthApi, Dropbox):
    api_base_uri = 'https://api-content.dropbox.com'

class LinkedinApi(OauthApi, Linkedin):
    def set_token(self, headers, params, token):
        params.update({ 'oauth2_access_token': token })

class RedditApi(OauthApi, Reddit):
    pass

class J0057TodoApi(OauthApi, J0057Todo):
    pass

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
                    'session': session_id in SESSIONS,
                    'tokens': {
                        'github': 'github_token' in session,
                        'facebook': 'facebook_token' in session,
                        'live': 'live_token' in session,
                        'google': 'google_token' in session,
                        'dropbox': 'dropbox_token' in session,
                        'linkedin': 'linkedin_token' in session,
                        'reddit': 'reddit_token' in session,
                    },
                    'request': { k: str(v) for (k, v) in request.items() }
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
