import webapp2
from google.appengine.ext import ndb
from template import template
from google.appengine.api import users

class ShortURL(ndb.Model):
	text = ndb.StringProperty()
	url = ndb.StringProperty()

class Create(webapp2.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			self.response.write(template('create_short_url.html'))
		else:
			self.redirect(users.create_login_url('/create_short_url'))
	def post(self):
		if not users.is_current_user_admin():
			return
		existing = ShortURL.query(ShortURL.text == self.request.get('text')).fetch(1)
		if len(existing) > 0:
			existing[0].key.delete()
		ShortURL(text = self.request.get('text'), url = self.request.get('url')).put()
		self.redirect(str(self.request.get('url')))

class Serve(webapp2.RequestHandler):
	def get(self, text):
		existing = ShortURL.query(ShortURL.text == text).fetch(1)
		if len(existing) > 0:
			self.redirect(str(existing[0].url))
		else:
			self.redirect('/')



