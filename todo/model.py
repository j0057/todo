 
import os

import data

def random(n=57):
    return os.urandom(n).encode('base64')[:-1].replace('+','_').replace('/','-')

class Model(object):
    def __init__(self, user_cookie=None, access_token=None):
        self.session = data.Session()
        if user_cookie:
            self.user_session = self.session.query(data.UserSession).filter_by(cookie=user_cookie).one()
        else:
            self.user_session = None

    def create_user(self, username, password1, password2):
        if password1 != password2:
            raise Exception("Passwords do not match")
        user = data.User(name=username, password=password1)
        self.session.add(user)
        self.session.commit()

    def create_user_session(self):
        user_session = data.UserSession(cookie=random())
        self.session.add(user_session)
        self.session.commit()
        return user_session.cookie

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

    def create_task(self, description):
        task = data.Task(description=description)
        self.user_session.user.tasks.append(task)
        self.session.commit()
        return task.task_id

    def get_tasks(self):
        return self.user_session.user.tasks

    def get_task(self, task_id):
        for task in self.user_session.user.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self, task_id, is_done, description):
        try:
            for task in self.user_session.user.tasks:
                if task.task_id == task_id:
                    task.is_done = is_done
                    task.description = description
                    return task
        finally:
            self.session.commit()

    def delete_task(self, task_id):
        for (i, task) in self.user_session.user.tasks:
            if task.task_id == task_id:
                del self.user_session.user.tasks[i]
                break
        self.session.commit()

