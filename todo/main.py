import json
import urllib

import pystache

import xhttp

from model import Model

class check_session(xhttp.decorator):
    def __call__(self, request, *a, **k):
        if not request['model'].validate_session():
            raise xhttp.HTTPException(xhttp.status.FORBIDDEN, { 'x-detail': 'No valid session found' })
        else:
            return self.func(request, *a, **k)

class Signup(xhttp.Resource):
    @xhttp.post({ 'username': r'^[a-z]+$', 'password1': r'^.+$', 'password2': r'^.+$' })
    def POST(self, request):
        try:
            request['model'].create_user(
                request['x-post']['username'],
                request['x-post']['password1'],
                request['x-post']['password2']
            )
            return {
                'x-status': xhttp.status.OK,
                'content-type': 'text/plain',
                'x-content': 'OK'
            }
        except Exception as e:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': e.message })

class Login(xhttp.Resource):
    @xhttp.post({ 'username': r'^[a-z]+$', 'password': r'^.+$' })
    def POST(self, request):
        username = request['x-post']['username']
        password = request['x-post']['password']
        if not request['model'].login(**request['x-post']):
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': 'Bad username or password' })
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'text/plain',
            'x-content': 'OK'
        }

class Tasks(xhttp.Resource):
    @check_session
    def GET(self, request):
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'application/json',
            'x-content': json.dumps(
                { 'tasks': [
                    { 'url': '/todo/tasks/{0}'.format(task.task_id),
                      'description': task.description,
                      'is_done': task.is_done }
                    for task in request['model'].get_tasks() ]
                })
        }

    @check_session
    @xhttp.post({ 'description': '^.+$' })
    def POST(self, request):
        task_id = request['model'].create_task(**request['x-post'])
        return {
            'x-status': xhttp.status.CREATED,
            'location': '/todo/tasks/{0}'.format(task_id),
            'x-content': 'Created',
            'content-type': 'text/plain'
        }

class Task(xhttp.Resource):
    @check_session
    def GET(self, request, task_id):
        task = request['model'].get_task(int(task_id))
        if not task:
            raise xhttp.HTTPException(xhttp.status.NOT_FOUND, 
                { 'x-detail': 'Task with id {0}'.format(task_id) })
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'application/json',
            'x-content': json.dumps({
                'description': task.description,
                'is_done': task.is_done,
                'url': '/todo/tasks/{0}'.format(task.task_id) }) }

    @check_session
    @xhttp.post({ 'is_done?': '^on|off|true|false$', 'description': '^.+$' })
    def PUT(self, request, task_id):
        task_id = int(task_id)
        request['x-post']['is_done'] = request['x-post']['is_done'] in ['true', 'on']
        task = request['model'].update_task(task_id, **request['x-post'])
        if not task:
            raise xhttp.HTTPException(xhttp.status.NOT_FOUND, 
                { 'x-detail': 'Task with id {0}'.format(task_id) })
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'application/json',
            'x-content': json.dumps({
                'description': task.description,
                'is_done': task.is_done,
                'url': '/todo/tasks/{0}'.format(task.task_id) }) }

    @check_session
    def DELETE(self, request, task_id):
        task_id = int(task_id)
        request['model'].delete_task(task_id)
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'text/plain',
            'x-content': 'OK'
        }

class Authorize(xhttp.Resource):
    @xhttp.get({ 'client_id': '^.+$', 
                 'redirect_uri': '^.+$',
                 'scope': '^$',
                 'state': '^.+$',
                 'response_type': '^code$' })
    def GET(self, request):
        app_session = request['model'].find_app_session(
            request['x-get']['client_id'],
            request['x-get']['redirect_uri'])

        # already authorized; redirect to redirect_uri
        if app_session:
            return {
                'x-status': xhttp.status.FOUND,
                'location': app_session.app.redirect_uri
                            + '?'
                            + urllib.urlencode({ 'code': app_session.code,
                                                 'state': request['x-get']['state'] }) 
            }

        # not yet authorized; serve authorization page
        else:
            app = request['model'].find_app(request['x-get']['client_id'])
            with open('static/templates/authorize.xhtml', 'r') as template:
                return {
                    'x-status': xhttp.status.OK,
                    'content-type': 'application/xhtml+xml; charset=utf-8',
                    'x-content': pystache.render(template.read(), {
                        'app_name': app.name,
                        'client_id': app.client_id,
                        'csrf_token': request['model'].generate_csrf_token(),
                        'state': request['x-get']['state']
                    }).encode('utf8')
                } 

    @xhttp.post({ 'csrf_token': '^.+$', 
                  'client_id': '^.+$',
                  'state': '^.+$',
                  'yes?': '^yes$', 
                  'no?': '^no$' })
    def POST(self, request):
        if not request['model'].validate_csrf_token(request['x-post']['csrf_token']):
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': 'Bad CSRF token' })

        app = request['model'].find_app(request['x-post']['client_id'])

        # authorization positive; redirect to callback_url with code
        if request['x-post']['yes']:
            app_session = request['model'].create_app_session(app.client_id, app.redirect_uri)
            return {
                'x-status': xhttp.status.FOUND,
                'location': app.redirect_uri
                            + '?'
                            + urllib.urlencode({ 'code': app_session.code, 'state': request['x-post']['state'] }) }

        # authorization negative; redirect to callback_url with error
        elif request['x-post']['no']:
            raise xhttp.HTTPException(xhttp.status.NOT_IMPLEMENTED)

        # something fishy is up
        else:
            raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': "You didn't press yes or no" })

class AccessToken(xhttp.Resource):
    @xhttp.post({ 'client_id': '^.+$',
                  'client_secret': '^.+$',
                  'code': '^.+$',
                  'redirect_uri': '^.+$',
                  'grant_type': '^authorization_code$' })
    def POST(self, request):
        app_session = request['model'].get_access_token(
            request['x-post']['client_id'],
            request['x-post']['client_secret'],
            request['x-post']['code'],
            request['x-post']['redirect_uri'])
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'application/json',
            'x-content': json.dumps({
                'access_token': app_session.cookie,
                'token_type': 'Bearer'
            })
        }

class session_generator(xhttp.decorator):
    def _redirect_cookie(self, request_uri, session_id=''):
        return {
            'x-status': xhttp.status.FOUND,
            'set-cookie': 'session_id={0}'.format(session_id),
            'location': request_uri,
            'content-type': 'text/plain',
            'x-content': 'Found' }

    @xhttp.cookie({ 'session_id?': '^.*$' })
    def __call__(self, request, *a, **k):
        # only for /todo/ requests
        if not request['x-request-uri'].startswith('/todo/'):
            return self.func(request, *a, **k)

        # load session from authorization header
        elif 'authorization' in request:
            request['model'] = Model(app_cookie=request['authorization'])
            return self.func(request, *a, **k)

        # load session from cookie
        elif request['x-cookie']['session_id']:
            request['model'] = Model(user_cookie=request['x-cookie']['session_id'])
            return self.func(request, *a, **k)

        # create session
        else:
            # only on GET requests
            if request['x-request-method'] == 'GET':
                session_id = Model().create_user_session()
                return self._redirect_cookie(request['x-request-uri'], session_id)
            # for PUT/POST/DELETE, ...just roll with it? see what happens?
            else:
                #raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': 'No session cookie found' })
                request['model'] = Model()
                return self.func(request, *a, **k)

class TodoRouter(xhttp.Router):
    def __init__(self):
        super(TodoRouter, self).__init__(
            (r'^/$',                            xhttp.Redirector('/todo/')),
            (r'^/todo/$',                       xhttp.Redirector('/todo/login.xhtml')),
            (r'^/todo/([a-z]+\.xhtml)$',        xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/todo/([a-z]+\.js)$',           xhttp.FileServer('static', 'application/javascript')),
            (r'^/todo/signup/$',                Signup()),
            (r'^/todo/login/$',                 Login()),
            (r'^/todo/tasks/$',                 Tasks()),
            (r'^/todo/tasks/([0-9]+)$',         Task()),
            (r'^/todo/authorize/',              Authorize()),
            (r'^/todo/access_token/',           AccessToken())
        )

    @xhttp.xhttp_app
    @xhttp.catcher
    @session_generator
    def __call__(self, request, *a, **k):
        return super(TodoRouter, self).__call__(request, *a, **k)

app = TodoRouter()
#app = session_generator(app)
#app = xhttp.catcher(app)
#app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app, port=8080)
