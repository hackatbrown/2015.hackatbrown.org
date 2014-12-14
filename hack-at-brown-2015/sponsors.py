import webapp2
from template import template

class Page(webapp2.RequestHandler):
	def get(self):
		self.response.write(template('sponsors.html'))
