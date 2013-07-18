from sqlalchemy import create_engine 
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Boolean, String, DateTime

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)

    name = Column(String, unique=True)

    email = Column(String)

    password = Column(String)

    def __repr__(self):
        return '<User {0}: {1}>'.format(self.user_id, self.name)

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)

    is_done = Column(Boolean, nullable=False, default=False)

    description = Column(String)

    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('User', backref=backref('tasks', order_by=task_id))

    def __repr__(self):
        return '<Task {0}: {1}>'.format(self.task_id, self.description)

class Session(Base):
    __tablename__ = 'sessions'

    session_id = Column(Integer, primary_key=True)

    cookie = Column(String)
    code = Column(String)

    last_active = Column(DateTime)

    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('User', backref=backref('sessions', order_by=session_id))

    app_id = Column(Integer, ForeignKey('apps.app_id'))
    app = relationship('App', backref=backref('sessions', order_by=session_id))

    def __repr__(self):
        return '<Session {0}: {1}>'.format(self.session_id, self.cookie)

class App(Base):
    __tablename__ = 'apps'

    app_id = Column(Integer, primary_key=True)

    name = Column(String)

    client_id = Column(String)
    client_secret = Column(String)
    callback_url = Column(String)

    developer_id = Column(Integer, ForeignKey('users.user_id'))
    developer = relationship('User', backref=backref('apps', order_by=app_id))

    def __repr__(self):
        return '<App {0}: {1}'.format(self.app_id, self.name)

engine = create_engine('sqlite:///db.dat', echo=False)

Base.metadata.create_all(engine)

Database = sessionmaker()
Database.configure(bind=engine)

if __name__ == '__main__':
    db = Database()
