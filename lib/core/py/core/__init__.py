#!/usr/bin/env python2.7

import sh

from router import Router
from resource import Resource
from redirector import Redirector
#rom dispatcher import Dispatcher

from easydict import EasyDict

from fileserver import FileServer, serve_file
from mergedfile import MergedFile

from basedec import BaseDecorator

from xsltdec import xslt
from pathinfodec import pathinfo

from catcher import catcher
from session import session_loader
from authdec import authenticated
from transformer import transformer
from partial import partial
from cached import cached

import report

import inifile
ini = inifile.INIFile('/home/joost/www/site.ini')
del inifile

def run_server(app):
    def fix_wsgiref(app):
        def fixed_app(request, start_response):
            if 'REQUEST_URI' not in request:
                request['REQUEST_URI'] = request['PATH_INFO']
                if request['QUERY_STRING']:
                    request['REQUEST_URI'] += '?'
                    request['REQUEST_URI'] += request['QUERY_STRING']
            import os
            request['DOCUMENT_ROOT'] = os.getcwd()
            return app(request, start_response)
        return fixed_app

    app = fix_wsgiref(app)

    print 'Serving on port 8000'
    import wsgiref.simple_server
    httpd = wsgiref.simple_server.make_server('', 8000, app)
    httpd.serve_forever()

def debug(request, message):
    if not message.endswith('\n'):
        message += '\n'
    request.environ['wsgi.errors'].write(message)

