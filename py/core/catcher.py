import traceback

import webob
import webob.dec
import webob.exc

try:
    from MySQLdb import MySQLError
except ImportError:
    class MySQLError(Exception):
        pass

def catcher(application):
	@webob.dec.wsgify
	def catcher_app(request):
		try:
			try:
				return application(request)
			except MySQLError as e:
				raise webob.exc.HTTPInternalServerError('{0}: {1}'.format(e[0], e[1]))
			except webob.exc.HTTPException:
				raise
			except Exception as e:
				msg = '{0} arguments: {1}\n\n{2}'.format(type(e).__name__, repr(e.args), traceback.format_exc(e))
				raise webob.exc.HTTPInternalServerError(msg,
					body_template_obj = webob.exc.Template('${explanation}<br/><br/><pre>${detail}</pre>${html_comment}'))
		except webob.exc.HTTPException as e:
			if request.is_xhr and 400 <= e.code < 599:
				return webob.Response(status=e.code,
									  content_type='text/plain; charset=UTF-8',
									  body='\n\n'.join([
										'{0} {1}'.format(e.code, e.title),
										e.explanation or '',
										e.detail or '']))
			else:
				raise e
	return catcher_app
