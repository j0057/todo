class BaseDecorator(object):
    def __init__(self, func):
        self.func = func
    def __get__(self, object, type=None):
        if type is None:
            return self
        newfunc = self.func.__get__(object, type)
        return self.__class__(newfunc)
