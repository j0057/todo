 
import os

import xhttp

import data

def random(n=57):
    return (os.urandom(n).encode('base64')
        .replace('\n', '')
        .replace('+', '_')
        .replace('/','-'))

class print_args(xhttp.decorator):
    def __call__(self, *a, **k):
        print self.func.__name__, a, k
        result = self.func(*a, **k)
        print self.func.__name__, ':', result
        return result

class ChattyObject(object):
    class __metaclass__(type):
        def __new__(cls, name, bases, attrs):
            attrs.update({ k: print_args(v) 
                           for (k, v) in attrs.items() 
                           if not k.startswith('__')
                           if callable(v) })
            return super(cls, cls).__new__(cls, name, bases, attrs)

class OAuthException(Exception):
    pass

class Model(ChattyObject):
    def __init__(self, user_cookie=None, app_cookie=None):
        self.db = data.Database()
        if user_cookie:
            self.cookie = user_cookie
        elif app_cookie and app_cookie.startswith('Bearer '):
            self.cookie = app_cookie.replace('Bearer ', '')
        else:
            self.cookie = None
        self._session = None

    @property
    def session(self):
        if self.cookie and not self._session:
            self._session = self.db \
                .query(data.Session) \
                .filter_by(cookie=self.cookie) \
                .first()
        return self._session

    def validate_session(self):
        if self.session is None:
            return False
        if self.session.user is None:
            return False
        return True

    def create_user_session(self):
        session = data.Session(cookie=random())
        self.db.add(session)
        self.db.commit()
        return session.cookie

    def create_user(self, username, password1, password2):
        if password1 != password2:
            raise Exception("Passwords do not match")
        user = data.User(name=username, password=password1)
        self.db.add(user)
        self.db.commit()
        return user

    def login(self, username, password):
        user = self.db \
            .query(data.User) \
            .filter_by(name=username) \
            .first()
        if user and user.password == password:
            self.session.user = user
            self.db.commit()
            return True
        return False

    def create_task(self, description):
        task = data.Task(description=description)
        self.session.user.tasks.append(task)
        self.db.commit()
        return task.task_id

    def get_tasks(self):
        return self.session.user.tasks

    def get_task(self, task_id):
        for task in self.session.user.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self, task_id, is_done, description):
        try:
            for task in self.session.user.tasks:
                if task.task_id == task_id:
                    task.is_done = is_done
                    task.description = description
                    return task
        finally:
            self.db.commit()

    def delete_task(self, task_id):
        for (i, task) in enumerate(self.session.user.tasks):
            if task.task_id == task_id:
                del self.session.user.tasks[i]
                break
        self.db.commit()

    def create_app(self, name, redirect_uri, client_id=None, client_secret=None):
        app = data.App(
            name=name, 
            redirect_uri=redirect_uri, 
            client_id=client_id or random(15), 
            client_secret=client_secret or random(),
            developer=self.session.user)
        self.db.add(app)
        self.db.commit()
        return app

    def find_app(self, client_id):
        return self.db.query(data.App).filter_by(client_id=client_id).first()

    def find_app_session(self, client_id, redirect_uri):
        for session in self.session.user.sessions:
            if not session.app:
                continue
            if session.app.client_id != client_id:
                continue
            if session.app.redirect_uri != redirect_uri:
                raise OAuthException('Invalid redirect URI')
            session.code = random(15)
            self.db.commit()
            return session
        return None

    def create_app_session(self, client_id, redirect_uri):
        app = self.db.query(data.App).filter_by(client_id=client_id).one()
        if app.redirect_uri != redirect_uri:
            return None # wrong redirect_uri 
        session = data.Session(
            code=random(15), 
            user=self.session.user,
            app=app)
        self.db.add(session)
        self.db.commit()
        return session

    def get_access_token(self, client_id, client_secret, code, redirect_uri):
        app = self.db.query(data.App).filter_by(client_id=client_id).first()
        if app is None:
            return None # wrong client_id
        if app.client_secret != client_secret:
            return None # wrong client_secret
        if app.redirect_uri != redirect_uri:
            return None # wrong redirect_uri
        for session in app.sessions:
            if session.code == code:  
                session.code = None
                session.cookie = random()
                self.db.commit()
                return session
        return None # wrong code

    def generate_csrf_token(self):
        self.session.csrf_token = random()
        self.db.commit()
        return self.session.csrf_token

    def validate_csrf_token(self, csrf_token):
        try:
            return self.session.csrf_token and self.session.csrf_token == csrf_token
        finally:
            self.session.csrf_token = None
            self.db.commit()
            
if __name__ == '__main__':
    cb = 'https://dev.j0057.nl/oauth/j0057-todo/code/'
    db = data.Database()
    model = Model()
    model.cookie = model.create_user_session()
    model.create_user('joost', 'foo', 'foo')
    model.create_user('foo', 'bar', 'bar')
    model.login('joost', 'foo')
    app = model.create_app('dev.j0057.nl', cb, 'test-id', 'test-secret')
    model.find_app_session(app.client_id, cb)
    session1 = model.create_app_session(app.client_id, cb)
    print 'code:', session1.code
    session2 = model.get_access_token(app.client_id, app.client_secret, session1.code, cb)
    print 'access_token:', session2.cookie

