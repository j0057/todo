import os
import uuid
import urlparse

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

SKYDRIVE_CLIENT_ID = os.environ.get('SKYDRIVE_CLIENT_ID', '')
SKYDRIVE_CLIENT_SECRET = os.environ.get('SKYDRIVE_CLIENT_SECRET', '')

print 'GITHUB_CLIENT_ID = {0!r}'.format(GITHUB_CLIENT_ID)
print 'GITHUB_CLIENT_SECRET = {0!r}'.format(GITHUB_CLIENT_SECRET)

print 'FACEBOOK_CLIENT_ID = {0!r}'.format(FACEBOOK_CLIENT_ID)
print 'FACEBOOK_CLIENT_SECRET = {0!r}'.format(FACEBOOK_CLIENT_SECRET)

print 'SKYDRIVE_CLIENT_ID = {0!r}'.format(SKYDRIVE_CLIENT_ID)
print 'SKYDRIVE_CLIENT_SECRET = {0!r}'.format(SKYDRIVE_CLIENT_SECRET)

#
# /oauth/skydrive
#

# 1. https://login.live.com/oauth20_authorize.srf
#    ?client_id=CLIENT_ID
#    &scope=SCOPES
#    &response_type=code
#    &redirect_uri=REDIRECT_URL
#
# 2. POST https://login.live.com/oauth20_token.srf
#    Content-type: application/x-www-form-urlencoded
#
#    client_id=CLIENT_ID
#    &redirect_uri=REDIRECT_URL
#    &client_secret=CLIENT_SECRET
#    &code=AUTHORIZATION_CODE
#    &grant_type=authorization_code

class SkydriveAuthorize(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    def GET(self, request):
        nonce = str(uuid.uuid4())
        SESSIONS[request['x-cookie']['session_id']]['skydrive_nonce'] = nonce
        print SESSIONS
        raise xhttp.HTTPException(xhttp.status.SEE_OTHER, {
            'location': 'https://login.live.com/oauth20_authorize.srf?client_id={0}&redirect_uri={1}&scope=wl.signin%20wl.basic&state={2}&response_type=code'.format(
                SKYDRIVE_CLIENT_ID, 
                'http://dev.j0057.nl/oauth/skydrive/callback/',
                nonce),
            'x-detail': 'Redirecting you to Skydrive...'
        })

class SkydriveCallback(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.get({ 'code': r'^([-_0-9a-zA-Z]+)$', 'state': r'^[-0-9a-f]+$' })
    def GET(self, request):
        session_id = request['x-cookie']['session_id']
        session = SESSIONS[session_id]
        state = request['x-get']['state']
        nonce = session.pop('skydrive_nonce')
        if state != nonce:
            raise xhttp.HTTPException(xhttp.BAD_REQUEST, { 'x-detail': 'Bad state {0}'.format(state) })
        code = request['x-get']['code']
        r = requests.post(
            'https://login.live.com/oauth20_token.srf',
            data={
                'client_id': SKYDRIVE_CLIENT_ID,
                'redirect_uri': 'http://dev.j0057.nl/oauth/skydrive/callback/',
                'client_secret': SKYDRIVE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            },
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
            })
        print '###', r.status_code, r.content
        data = r.json()
        session['skydrive_token'] = data['access_token']
        print SESSIONS
        return { 
            'x-status': xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml'
        }

class SkydriveRequest(xhttp.Resource):
    pass

#
# /oauth/facebook
#

class FacebookAuthorize(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    def GET(self, request):
        nonce = str(uuid.uuid4())
        SESSIONS[request['x-cookie']['session_id']]['facebook_nonce'] = nonce
        print SESSIONS
        raise xhttp.HTTPException(xhttp.status.SEE_OTHER, {
            'location': 'https://www.facebook.com/dialog/oauth?client_id={0}&redirect_uri=http://dev.j0057.nl/oauth/facebook/callback/&scope=&state={1}'.format(FACEBOOK_CLIENT_ID, nonce),
            'x-detail': 'Redirecting you to Facebook...'
        })

class FacebookCallback(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.get({ 'code': r'^([-_0-9a-zA-Z]+)$', 'state': r'^[-0-9a-f]+$' })
    def GET(self, request):
        session_id = request['x-cookie']['session_id']
        session = SESSIONS[session_id]
        state = request['x-get']['state']
        nonce = session.pop('facebook_nonce')
        if state != nonce:
            raise xhttp.HTTPException(xhttp.BAD_REQUEST, { 'x-detail': 'Bad state {0}'.format(state) })
        code = request['x-get']['code']
        r = requests.post(
            'https://graph.facebook.com/oauth/access_token',
            params={
                'client_id': FACEBOOK_CLIENT_ID,
                'redirect_uri': 'http://dev.j0057.nl/oauth/facebook/callback/',
                'client_secret': FACEBOOK_CLIENT_SECRET,
                'code': code
            },
            headers={
                'accept': 'application/json'
            })
        data = urlparse.parse_qs(r.content)
        session['facebook_token'] = data['access_token'][0]
        print SESSIONS
        return { 
            'x-status': xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml'
        }

class FacebookRequest(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.get({ 'fields?': r'^.*$' })
    def GET(self, request, path):
        session_id = request['x-cookie']['session_id']
        session = SESSIONS[session_id]
        path = 'https://graph.facebook.com/' + path
        params = { 'access_token': session.get('facebook_token', '') }
        params.update(request['x-get'])
        r = requests.get(
            path,
            params=params,
            headers={
                'accept': 'application/json'
            })
        return {
            'x-status': r.status_code,
            'content-type': r.headers['content-type'],
            'x-content': r.content
        }


# /me?fields=name,friends.fields(name,username),username

#
# /oauth/github
#

class GithubAuthorize(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    def GET(self, request):
        nonce = str(uuid.uuid4())
        SESSIONS[request['x-cookie']['session_id']]['github_nonce'] = nonce
        print SESSIONS
        raise xhttp.HTTPException(xhttp.status.SEE_OTHER, {
            'location': 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri=http://dev.j0057.nl/oauth/github/callback/&scope=&state={1}'.format(GITHUB_CLIENT_ID, nonce),
            'x-detail': 'Redirecting you to Github...'
        })

class GithubCallback(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    @xhttp.get({ 'code': r'^([0-9a-z]+)$', 'state': r'^[-0-9a-f]+$' })
    def GET(self, request):
        session_id = request['x-cookie']['session_id']
        session = SESSIONS[session_id]
        state = request['x-get']['state']
        nonce = session.pop('github_nonce')
        if state != nonce:
            raise xhttp.HTTPException(xhttp.BAD_REQUEST, { 'x-detail': 'Bad state {0}'.format(state) })
        code = request['x-get']['code']
        r = requests.post('https://github.com/login/oauth/access_token',
            params={ 
                'client_id': GITHUB_CLIENT_ID, 
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code
            },
            headers={
                'accept': 'application/json'
            })
        data = r.json()
        session['github_token'] = data['access_token']
        print SESSIONS
        return {
            'x-status': xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml'
        }

class GithubRequest(xhttp.Resource):
    @xhttp.cookie({ 'session_id': '^(.+)$' })
    def GET(self, request, path):
        session_id = request['x-cookie']['session_id']
        session = SESSIONS[session_id]
        path = 'https://api.github.com/' + path
        print path
        r = requests.get(
            path,
            params={
                'access_token': session.get('github_token', '')
            },
            headers={
                'accept': 'application/json'
            })
        return {
            'x-status': r.status_code,
            'content-type': r.headers['content-type'],
            'x-content': r.content
        }
        

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
            (r'^/oauth/$',                      xhttp.Redirector('index.xhtml')),
            (r'^/oauth/(.*\.xhtml)$',           xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/oauth/(.*\.js)$',              xhttp.FileServer('static', 'application/javascript')),
            (r'^/oauth/skydrive/authorize/$',   SkydriveAuthorize()),
            (r'^/oauth/skydrive/callback/$',    SkydriveCallback()),
            (r'^/oauth/skydrive/request/(.*)$', SkydriveRequest()),
            (r'^/oauth/facebook/authorize/$',   FacebookAuthorize()),
            (r'^/oauth/facebook/callback/$',    FacebookCallback()),
            (r'^/oauth/facebook/request/(.*)$', FacebookRequest()),
            (r'^/oauth/github/authorize/$',     GithubAuthorize()),
            (r'^/oauth/github/callback/$',      GithubCallback()),
            (r'^/oauth/github/request/(.*)$',   GithubRequest()),
            (r'^/oauth/session/start/$',        SessionStart()),
            (r'^/oauth/session/delete/$',       SessionDelete()),
            (r'^/oauth/session/check/$',        SessionCheck())
        )

app = OauthRouter()
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app)
