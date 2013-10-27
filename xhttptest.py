#!/usr/bin/env python

import re
import sys

if sys.version_info[0] == 3:
    from urllib.parse import unquote
elif sys.version_info[0] == 2:
    from urllib import unquote

import xhttp

# wsgi
def hello_world_1(env, start_response):
    start_response("200 OK", [("Content-Type", "text-plain")])
    yield "Hello, world!\n"


# wsgi
def env_1(env, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    for k in sorted(env.keys()):
        yield "{0:40} = {1}\n".format(k, repr(env[k]))


# xhttp
def env_2(req, *a, **k):
    def response_generator():
        for k in sorted(req.keys()):
            if k == "x-env": continue
            yield "{0:40}: {1}\n".format(k.title(), repr(req[k]))
        yield "\n\n"
        for k in sorted(req["x-env"].keys()):
            yield "{0:40} = {1}\n".format(k, repr(req["x-env"][k]))
        yield "\n\n"
    return {
        "x-status"     : xhttp.status.OK,
        "x-content"    : response_generator(),
        "content-type" : "text/plain" 
    }


# xhttp
def hello_world_2(req):
    return {
        "x-status"     : 200,
        "x-content"    : "Hello, world!\n",
        "content-type" : "text/plain"
    }


# xhttp resource
class HelloWorld(xhttp.Resource):
    @xhttp.accept_charset
    @xhttp.accept
    def GET(self, req):
        greeting = { 
            "message": "Hello, world!" 
        }
        greeting_view = {
            "text/plain"            : lambda m: m["message"],
            "text/html"             : lambda m: ["p", m["message"]],
            "application/json"      : lambda m: m,
            "application/xhtml+xml" : lambda m: ["p", ("xmlns", "http://www.w3.org/1999/xhtml"), 
                                        m["message"], 
                                        ["br"],
                                        req["x-path-info"]],
            "application/xml"       : lambda m: ["message", m["message"]] 
        }
        return {
            "x-status"       : 200,
            "x-content"      : greeting,
            "x-content-view" : greeting_view
        }

# wsgi 
class HelloWorldApp_1(xhttp.WSGIAdapter, HelloWorld):
    pass

# wsgi
class HelloWorldApp_2(HelloWorld):
    __metaclass__ = xhttp.as_wsgi_app

# wsgi
class HelloWorldApp_3(HelloWorld):
    __metaclass__ = xhttp.extended_with(xhttp.WSGIAdapter)

# wsgi
class TestRouter(xhttp.Router):
    def __init__(self):
        super(TestRouter, self).__init__(
            (r"^/$",                            xhttp.Redirector("/xhttptest/")),
            (r"^/xhttptest/$",                  xhttp.Redirector("/xhttptest/test/")),
            (r"^/xhttptest/test/$",             hello_world_2),
            (r"^/xhttptest/env/(.*)$",          env_2),
            (r"^/xhttptest/hello-world/$",      HelloWorld()),
            (r"^/xhttptest/hw/$",               HelloWorld()),
            (r"^/xhttptest/debug/(.*)$",        self.debug)
        )

    def debug(self, req, virt_path):
        dump_dict = lambda d: "\n".join("{0:20} = {1}".format(k, repr(d[k])) for k in sorted(d.keys()))

        req['x-path-info'] = "/" + virt_path 
        req['x-request-uri'] = req['x-path-info']
        if req['x-query-string']:
            req['x-request-uri'] += '?' + req['x-query-string']
        res = self(req)
        content = dump_dict({k:v for k,v in req.items() if k!="x-env"}) \
            + "\n\n" \
            + dump_dict(res) \
            + "\n\n"
        return {
            "x-status": xhttp.status.OK,
            "x-content": [content],
            "content-type": "text/plain",
            "content-length": len(content)
        }

app = TestRouter()
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == "__main__":
    xhttp.run_server(app)

