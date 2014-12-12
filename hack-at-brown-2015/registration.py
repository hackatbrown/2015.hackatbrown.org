from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import json
import logging
import datetime
from send_email import send_email
from template import template
from google.appengine.api import memcache
import os
import base64
import webapp2

memcache_expiry = 10 * 60

class Hacker(ndb.Model):
	name = ndb.StringProperty()
	school = ndb.StringProperty()
	year = ndb.StringProperty()
	email = ndb.StringProperty()
	shirt_gen = ndb.StringProperty()
	shirt_size = ndb.StringProperty()
	dietary_restrictions = ndb.StringProperty()
	resume = ndb.BlobKeyProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	links = ndb.StringProperty(default=None)
	teammates = ndb.StringProperty(default=None)
	hardware_hack = ndb.StringProperty()
	first_hackathon = ndb.StringProperty()


	secret = ndb.StringProperty()

	admit_priority = ndb.FloatProperty(default=0)
	admitted_email_sent_date = ndb.DateTimeProperty()

	waitlist_email_sent_date = ndb.DateTimeProperty()

	rsvpd = ndb.BooleanProperty(default=False)
	checked_in = ndb.BooleanProperty(default=False)

	@classmethod
	def WithSecret(cls, secret):
		results = cls.query(cls.secret == secret).fetch(1)
		return results[0] if len(results) else None

def generate_secret_for_hacker_with_email(email):
	return base64.urlsafe_b64encode(email.encode('utf-8') + ',' + os.urandom(64))

def accept_hacker(hacker):
	logging.debug("addmitting a hacker\n")
	email = template("emails/admitted.html", {"hacker": hacker})
	send_email(recipients=[hacker.email], html=email, subject="We'd like to invite you to Hack@Brown")

	hacker.admitted_email_sent_date = datetime.datetime.now()
	hacker.put()
	memcache.add("admitted:{0}".format(hacker.key.id()), "1", memcache_expiry)

class RegistrationHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		hacker = Hacker()

		for key in ['name', 'school', 'year', 'email', 'shirt_size', 'shirt_gen', 'dietary_restrictions', 'teammates', 'hardware_hack', 'links', 'first_hackathon']:
			print key + " " + self.request.get(key)
			setattr(hacker, key, self.request.get(key))
		if Hacker.query(Hacker.email == hacker.email).count() > 0:
			self.response.write(json.dumps({"success":False}))
			return
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

class CheckRegistrationHandler(webapp2.RequestHandler):
	def get(self):
		email = self.request.get('email')
		if Hacker.query(Hacker.email == email).count() > 0:
				self.response.write(json.dumps({"registered":True}))
		else:
			self.response.write(json.dumps({"registered":False}))
		