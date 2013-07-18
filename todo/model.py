 
import os

import xhttp

import data

def random(n=57):
    return os.urandom(n).encode('base64')[:-1].replace('+','_').replace('/','-')

class print_args(xhttp.decorator):
    def __call__(self, *a, **k):
        print self.func.__name__, a, k
        result = self.func(*a, **k)
        print self.func.__name__, ':', result
        return result

class Model(object):
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

    @print_args
    def create_user_session(self):
        session = data.Session(cookie=random())
        self.db.add(session)
        self.db.commit()
        return session.cookie

    @print_args
    def create_user(self, username, password1, password2):
        if password1 != password2:
            raise Exception("Passwords do not match")
        user = data.User(name=username, password=password1)
        self.db.add(user)
        self.db.commit()

    @print_args
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

    @print_args
    def create_task(self, description):
        task = data.Task(description=description)
        self.session.user.tasks.append(task)
        self.db.commit()
        return task.task_id

    @print_args
    def get_tasks(self):
        return self.session.user.tasks

    @print_args
    def get_task(self, task_id):
        for task in self.session.user.tasks:
            if task.task_id == task_id:
                return task
        return None

    @print_args
    def update_task(self, task_id, is_done, description):
        try:
            for task in self.session.user.tasks:
                if task.task_id == task_id:
                    task.is_done = is_done
                    task.description = description
                    return task
        finally:
            self.db.commit()

    @print_args
    def delete_task(self, task_id):
        for (i, task) in enumerate(self.session.user.tasks):
            if task.task_id == task_id:
                del self.session.user.tasks[i]
                break
        self.db.commit()

    @print_args
    def create_app(self, name, callback_url):
        app = data.App(name=name, callback_url=callback_url, client_id=random(9), client_secret=random(),
                       developer=self.session.user)
        self.db.add(app)
        self.db.commit()
        return app

    @print_args
    def find_app_session(self, client_id, callback_url):
        for session in self.session.user.sessions:
            if not session.app:
                continue
            if session.app.client_id == client_id:
                return session
        return None

    @print_args
    def create_app_session(self, client_id, callback_url):
        app = self.db.query(data.App).filter_by(client_id=client_id).one()
        if app.callback_url != callback_url:
            return None # wrong callback url
        session = data.Session(
            code=random(15), 
            user=self.session.user,
            app=)
        self.db.add(session)
        self.db.commit()
        return session

    @print_args
    def get_access_token(self, client_id, client_secret, code, callback_url):
        app = self.db.query(data.App).filter_by(client_id=client_id).first()
        if app is None:
            return None # wrong client_id
        if app.client_secret != client_secret:
            return None # wrong client_secret
        if app.callback_url != callback_url:
            return None # wrong callback_url
        for session in app.sessions:
            if session.code == code:  
                session.code = None
                session.cookie = random()
                self.db.commit()
                return session
        return None # wrong code
            
if __name__ == '__main__':
    cb = 'https://dev.j0057.nl/oauth/todo/code/'
    db = data.Database()
    model = Model()
    model.cookie = model.create_user_session()
    model.create_user('joost', 'foo', 'foo')
    model.login('joost', 'foo')
    app = model.create_app('dev.j0057.nl', cb)
    model.find_app_session(app.client_id, cb)
    session1 = model.create_app_session(app.client_id, cb)
    print 'code:', session1.code
    session2 = model.get_access_token(app.client_id, app.client_secret, session1.code, cb)
    print 'access_token:', session2.cookie

