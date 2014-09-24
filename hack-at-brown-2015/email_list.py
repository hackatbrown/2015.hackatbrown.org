import webapp2
from google.appengine.ext import ndb
import json

class EmailListEntry(ndb.Model):
  email = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

  @classmethod
  def add_email(cls, email_address):
		existing = EmailListEntry.query(EmailListEntry.email == email_address).fetch()
		if existing == []:
			entry = EmailListEntry(email=email_address)
			entry.put()
			return True
		else:
			return False

class SignUpForUpdatesHandler(webapp2.RequestHandler):
	def post(self):
		EmailListEntry.add_email(self.request.get('email'))
		self.response.write(json.dumps({"success": True}))
