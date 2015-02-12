import webapp2
from template import template

class Handler(webapp2.RequestHandler):
	def get(self):
		param = {}
		self.response.write(template("bigboard.html", params))