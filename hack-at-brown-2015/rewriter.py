import urlparse
import wsgiref

class WSGIMiddleware:
	def __init__(self, app):
		self.app = app

	def __call__(self, environ, start_response):
		env = dict(environ)
		query = urlparse.parse_qs(env['QUERY_STRING'])
		if 'dayof' in query or env['HTTP_HOST'].startswith('at.'):
			env['PATH_INFO'] = '/dayof' + env['PATH_INFO']
			if env['PATH_INFO'][-1] == '/': env['PATH_INFO'] = env['PATH_INFO'][:-1]
		return self.app(env, start_response)
		