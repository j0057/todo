 
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
    def __init__(self, user_cookie=None, access_token=None):
        self.session = data.Session()
        self.user_cookie = user_cookie
        self._user_session = None

    @property
    def user_session(self):
        if self.user_cookie and not self._user_session:
            self._user_session = self.session \
                .query(data.UserSession) \
                .filter_by(cookie=self.user_cookie) \
                .first()
        return self._user_session

    @print_args
    def create_user(self, username, password1, password2):
        if password1 != password2:
            raise Exception("Passwords do not match")
        user = data.User(name=username, password=password1)
        self.session.add(user)
        self.session.commit()

    @print_args
    def create_user_session(self):
        user_session = data.UserSession(cookie=random())
        self.session.add(user_session)
        self.session.commit()
        return user_session.cookie

    @print_args
    def login(self, username, password):
        user = self.session \
            .query(data.User) \
            .filter_by(name=username) \
            .first()
        if user and user.password == password:
            self.user_session.user = user
            self.session.commit()
            return True
        return False

    @print_args
    def create_task(self, description):
        task = data.Task(description=description)
        self.user_session.user.tasks.append(task)
        self.session.commit()
        return task.task_id

    @print_args
    def get_tasks(self):
        return self.user_session.user.tasks

    @print_args
    def get_task(self, task_id):
        for task in self.user_session.user.tasks:
            if task.task_id == task_id:
                return task
        return None

    @print_args
    def update_task(self, task_id, is_done, description):
        try:
            for task in self.user_session.user.tasks:
                if task.task_id == task_id:
                    task.is_done = is_done
                    task.description = description
                    return task
        finally:
            self.session.commit()

    @print_args
    def delete_task(self, task_id):
        for (i, task) in enumerate(self.user_session.user.tasks):
            if task.task_id == task_id:
                del self.user_session.user.tasks[i]
                break
        self.session.commit()

