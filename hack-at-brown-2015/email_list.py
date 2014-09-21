import webapp2
from google.appengine.ext import ndb

class EmailListEntry(ndb.Model):
  email = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

  @classmethod
  def add_email(cls, email_address):
		existing = EmailListEntry.query(EmailListEntry.email == email_address).fetch()
		if existing == None:
			entry = EmailListEntry(email=email_address)
			entry.put()

class SignUpForUpdatesHandler(webapp2.RequestHandler):
	def post(self):
		email = self.request.get('email')
		EmailListEntry.add_email(email)
		self.redirect('/#gotcha')
