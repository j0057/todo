import json

import xhttp

from model import Model

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
    def GET(self, request):
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'application/json',
            'x-content': json.dumps([
                { 'url': '/todo/tasks/{0}'.format(task.task_id),
                  'description': task.description,
                  'is_done': task.is_done }
                for task in request['model'].get_tasks() ])
        }

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

    @xhttp.post({ 'is_done': '^true|false$', 'description': '^.+$' })
    def PUT(self, request, task_id):
        task_id = int(task_id)
        request['x-post']['is_done'] = request['x-post']['is_done'] == 'true'
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

    def DELETE(self, request, task_id):
        task_id = int(task_id)
        request['model'].delete_task(task_id)
        return {
            'x-status': xhttp.status.OK,
            'content-type': 'text/plain',
            'x-content': 'OK'
        }

class SessionGenerator(xhttp.decorator):
    @xhttp.cookie({ 'session_id?': '^.*$' })
    def __call__(self, request, *a, **k):
        if not request['x-cookie']['session_id']:
            if request['x-request-method'] == 'GET':
                session_id = Model().create_user_session()
                return {
                    'x-status': xhttp.status.FOUND,
                    'set-cookie': 'session_id={0}'.format(session_id),
                    'location': request['x-request-uri'],
                    'content-type': 'text/plain',
                    'x-content': 'Found'
                }
            else:
                raise xhttp.HTTPException(xhttp.status.BAD_REQUEST, { 'x-detail': 'No session cookie found' })
        else:
            request['model'] = Model(user_cookie=request['x-cookie']['session_id'])
            return self.func(request, *a, **k)

class TodoRouter(xhttp.Router):
    def __init__(self):
        super(TodoRouter, self).__init__(
            (r'^/$',                    xhttp.Redirector('/todo/')),
            (r'^/todo/$',               xhttp.Redirector('/todo/login.xhtml')),
            (r'^/todo/(.+\.xhtml)$',    xhttp.FileServer('static', 'application/xhtml+xml')),
            (r'^/todo/(.+\.js)$',       xhttp.FileServer('static', 'application/javascript')),
            (r'^/todo/signup/$',        Signup()),
            (r'^/todo/login/$',         Login()),
            (r'^/todo/tasks/$',         Tasks()),
            (r'^/todo/tasks/([0-9]+)$', Task())
        )

app = TodoRouter()
app = SessionGenerator(app)
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app, port=8080)
