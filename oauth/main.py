import uuid

import requests

import jjm.xhttp

SESSIONS = {}

GITHUB_CLIENT_ID = '92b6d47b724dc8d2628d'
GITHUB_CLIENT_SECRET = '9a3def19ec3f8bbe92cad64e46b5b55e10c4518b'

def parse_cookie(request):
    if 'cookie' in request:
        return { parts[0]: parts[1]
                 for parts in request['cookie'].split('; ') }
    else:
        return {}

class GithubRedirect(jjm.xhttp.Resource):
    def GET(self, request):
        raise jjm.xhttp.HTTPException(jjm.xhttp.status.SEE_OTHER, {
            'location': 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri=http://dev.j0057.nl/oauth/github_callback/&scope=&state='.format(GITHUB_CLIENT_ID),
            'x-detail': 'Redirecting you to Github...'
        })

class GithubCallback(jjm.xhttp.Resource):
    @jjm.xhttp.get({ 'code': r'^([0-9a-z]+)$' })
    def GET(self, request):
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
        return {
            'x-status': jjm.xhttp.status.SEE_OTHER,
            'set-cookie': 'github={0}; Path=/oauth'.format(data['access_token']),
            'location': '/oauth/index.xhtml'
        }

class SessionInitialize(jjm.xhttp.Resource):
    def GET(self, request):
        session_id = uuid.uuid4()
        SESSIONS[session_id] = {}
        return {
            'x-status': jjm.xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml',
            'set-cookie': 'session_id={0}; Path=/oauth'.format(session_id)
        }

class SessionDelete(jjm.xhttp.Resource):
    def GET(self, request):
        return {
            'x-status': jjm.xhttp.status.SEE_OTHER,
            'location': '/oauth/index.xhtml',
            'set_cookie': 'session_id=X; Path=/oauth; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        }

class OauthRouter(jjm.xhttp.Router):
    def __init__(self):
        super(OauthRouter, self).__init__(
            (r'^/$',                            jjm.xhttp.Redirector('/oauth')),
            (r'^/oauth/$',                      jjm.xhttp.Redirector('index.xhtml')),
            (r'^/oauth/(.*\.xhtml)$',           jjm.xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/oauth/github_callback/$',      GithubCallback()),
            (r'^/oauth/github/$',               GithubRedirect()),
            (r'^/oauth/session/initialize/$',   SessionInitialize()),
            (r'^/oauth/session/delete/$',       SessionDelete()),
            
        )

app = OauthRouter()
app = jjm.xhttp.catcher(app)
app = jjm.xhttp.xhttp_app(app)

if __name__ == '__main__':
    jjm.xhttp.run_server(app)
