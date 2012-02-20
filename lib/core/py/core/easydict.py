class EasyDict(dict):
    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value
        return self
    def __delattr__(self, name):
        del self[name]
        return self

if __name__ == '__main__':
    a = EasyDict(a=1, b=2, c='abc')

    b1 = EasyDict(a=1, b=2, c='abc')
    b2 = EasyDict(a=1, b=3, c='abc')
    b3 = EasyDict(a=1, b=2, c='def')
    b4 = EasyDict(a=1)

    print a == b1
    print a == b2
    print a == b3
    print a == b4


