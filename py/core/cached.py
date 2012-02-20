
import basedec 

def cached(size):
    def closure(SIZE, CACHE, KEYS):
        class cached(basedec.BaseDecorator):
            def __init__(self, func):
                self.func = func
            def __call__(self, request, *a, **k):
                key = hash(a)
                core.debug(request, 'Cache({0}): Cache object is 0x{1:x}'.format(SIZE, id(CACHE)))
                core.debug(request, 'Cache({0}): Checking for key {1:x}'.format(SIZE, key))
                if key in CACHE:
                    core.debug(request, 'Cache({0}): Hit key {1:x}'.format(SIZE, key))
                else:
                    core.debug(request, 'Cache({0}): Miss key {1:x}'.format(SIZE, key))
                    CACHE[key] = self.func(request, *a, **k)
                    KEYS.append(key)
                    if len(KEYS) > SIZE:
                        oldest = KEYS.pop()
                        core.debug(request, 'Cache({0}): Purging key {1:x}'.format(SIZE, oldest))
                        del CACHE[oldest]
                CACHE[key].body_stream.seek(0)
                return CACHE[key]
        return cached
    cache, keys = {}, []
    return closure(size, cache, keys)

