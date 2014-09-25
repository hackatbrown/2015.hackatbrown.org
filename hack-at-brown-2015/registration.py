from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import json
from send_email import send_email
from template import template
import os
import base64

class Hacker(ndb.Model):
	name = ndb.StringProperty()
	school = ndb.StringProperty()
	year = ndb.StringProperty()
	email = ndb.StringProperty()
	shirt_size = ndb.StringProperty()
	dietary_restrictions = ndb.StringProperty()
	resume = ndb.BlobKeyProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	
	secret = ndb.StringProperty()
		
	admit_priority = ndb.FloatProperty(default=0)
	admitted_email_sent_date = ndb.DateTimeProperty()
	
	waitlist_email_sent_date = ndb.DateTimeProperty()
	
	rsvpd = ndb.BooleanProperty(default=False)
	
	@classmethod
	def WithSecret(cls, secret):
		results = cls.query(cls.secret == secret).fetch(1)
		return results[0] if len(results) else None

def generate_secret_for_hacker_with_email(email):
	return base64.urlsafe_b64encode(email.encode('utf-8') + ',' + os.urandom(64))

class RegistrationHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		hacker = Hacker()
		for key in ['name', 'school', 'year', 'email', 'shirt_size', 'dietary_restrictions']:
			setattr(hacker, key, self.request.get(key))
		resume_files = self.get_uploads('resume')
		if len(resume_files) > 0:
			hacker.resume = resume_files[0].key()
		hacker.secret = generate_secret_for_hacker_with_email(hacker.email)
		hacker.put()
		
		email_html = template("emails/confirm_registration.html", {"name": hacker.name.split(" ")[0], "hacker": hacker})
		send_email(recipients=[hacker.email], subject="You've applied to Hack@Brown!", html=email_html)
		
		name = hacker.name.split(" ")[0] # TODO: make it better
		confirmation_html = template("post_registration_splash.html", {"name": name})
		self.response.write(json.dumps({"success": True, "replace_splash_with_html": confirmation_html}))
