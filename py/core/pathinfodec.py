import basedec

def pathinfo(pattern):
    class pathinfo(basedec.BaseDecorator):
        def __init__(self, func):
            self.func = func
            self.pattern = pattern

        def __call__(self, request):
            match = re.match(pattern, request.path_info)
            return self.func(request, *match.groups())
    return pathinfo
