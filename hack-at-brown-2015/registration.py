from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import json
from send_email import send_email
from template import template

class Hacker(ndb.Model):
	name = ndb.StringProperty()
	school = ndb.StringProperty()
	year = ndb.StringProperty()
	email = ndb.StringProperty()
	shirt_size = ndb.StringProperty()
	dietary_restrictions = ndb.StringProperty()
	resume = ndb.BlobKeyProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	
	admit_priority = ndb.FloatPropery(default=0)
	admitted = ndb.BooleanProperty(default=False)
	admitted_email_sent_date = ndb.DateTimeProperty()
	
	rsvpd = ndb.BooleanProperty(default=False)

class RegistrationHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		hacker = Hacker()
		for key in ['name', 'school', 'year', 'email', 'shirt_size', 'dietary_restrictions']:
			setattr(hacker, key, self.request.get(key))
		resume_files = self.get_uploads('resume')
		if len(resume_files) > 0:
			hacker.resume = resume_files[0].key()
		hacker.put()
		
		email_html = template("emails/confirm_registration.html", {"name": hacker.name.split(" ")[0]})
		send_email(recipients=[hacker.email], subject="You've applied to Hack@Brown!", html=email_html)
		
		self.response.write(json.dumps({"success": True}))
