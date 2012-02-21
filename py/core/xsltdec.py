import webob
import webob.exc

import StringIO

import xml
import basedec

class xslt(basedec.BaseDecorator):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args):
        response = self.func(request, *args)
        if 'xsl' in request.GET:
            self.link_stylesheet(request, response)
            response.content_type = 'application/xml; charset=UTF-8'
        elif 'xslt' in request.GET:
            self.apply_stylesheet(request, response)
            response.content_type = 'text/html; charset=UTF-8'
        else:
            self.serialize_xml(response)
            response.content_type = 'application/xml; charset=UTF-8'
        return response

    def link_stylesheet(self, request, response):
        response.body = xml.serialize_ws(
            [xml.FRAGMENT,
                [xml.PROCINC, 'xml', ('version', '1.0'), ('encoding', 'UTF-8')],
                [xml.PROCINC, 'xml-stylesheet', ('type', 'text/xsl'), ('href', request.GET['xsl'])],
                response.body]).encode('utf8')

    def apply_stylesheet(self, request, response):
        import lxml.etree
        self.serialize_xml(response)
        xsl = lxml.etree.XSLT(lxml.etree.parse(request.environ['DOCUMENT_ROOT'] + '/web/' + request.GET['xslt']))
        xml = lxml.etree.parse(StringIO.StringIO(response.body))
        response.body = str(xsl(xml))

    def serialize_xml(self, response):
        response.body = xml.serialize_ws(response.body).encode('utf8')
