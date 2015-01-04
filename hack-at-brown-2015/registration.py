from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import json
import logging
import datetime
from send_email import send_email
from email_list import EmailListEntry
from template import template
from google.appengine.api import memcache
import os
import base64
import webapp2
#Validation
from google.appengine.ext import blobstore
from google.appengine.api import datastore_errors
from template import utils



memcache_expiry = 10 * 60
hacker_keys = ['name', 'school', 'year', 'email', 'shirt_size', 'shirt_gen', 'dietary_restrictions', 'teammates', 'hardware_hack', 'links', 'first_hackathon', 'phone_number']
personal_info_keys = ['name', 'email', 'teammates', 'links', 'phone_number']

def stringValidator(prop, value):
		cleanValue = value.strip()

		if prop._name == 'email':
				cleanValue = cleanValue.lower()

		return cleanValue

def phoneValidator(prop, value):
	numbers = ''.join([c for c in value if c in '0123456789'])
	if len(numbers) == 0:
		return None
	elif len(numbers) == 10:
		return numbers
	elif len(numbers) == 11 and numbers[0] == '1':
		return numbers[1:] # remove +1 US country code
	else:
		raise datastore_errors.BadValueError(prop._name)

class Hacker(ndb.Model):
	#TODO: If you add a new property, please remember to add that property to deletedHacker.py.

	name = ndb.StringProperty(validator=stringValidator)
	school = ndb.StringProperty(validator=stringValidator)
	year = ndb.StringProperty(choices=['highschool', 'freshman', 'sophomore', 'junior', 'senior', 'grad_student'])
	email = ndb.StringProperty(validator=stringValidator)
	shirt_gen = ndb.StringProperty(choices=['M', 'W'])
	shirt_size = ndb.StringProperty(choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])
	dietary_restrictions = ndb.StringProperty(validator=stringValidator)
	resume = ndb.BlobKeyProperty()
	receipts = ndb.BlobKeyProperty(repeated=True)
	date = ndb.DateTimeProperty(auto_now_add=True)
	links = ndb.StringProperty(default=None)
	teammates = ndb.StringProperty(default=None, validator=stringValidator)
	teammates_emailed = ndb.BooleanProperty(default=False)
	hardware_hack = ndb.StringProperty(choices=["yes", 'no'])
	first_hackathon = ndb.StringProperty(choices=['yes', 'no'])


	phone_number = ndb.StringProperty(validator=phoneValidator) # normalized to only digits, no country code
	def pretty_phone(self):
		if self.phone_number:
			return "({0}) {1}-{2}".format(self.phone_number[:3], self.phone_number[3:6], self.phone_number[6:])
		else:
			return None

	secret = ndb.StringProperty()

	admit_priority = ndb.FloatProperty(default=0)
	admitted_email_sent_date = ndb.DateTimeProperty()
	post_registration_email_sent_date = ndb.DateTimeProperty()

	waitlist_email_sent_date = ndb.DateTimeProperty()

	rsvpd = ndb.BooleanProperty(default=False)
	checked_in = ndb.BooleanProperty(default=False)

	ip = ndb.StringProperty()

	#Only collected for reimbursements.
	address1 = ndb.StringProperty()
	address2 = ndb.StringProperty()
	city = ndb.StringProperty()
	state = ndb.StringProperty()
	zip = ndb.StringProperty()
	country =ndb.StringProperty()

	@classmethod
	def WithSecret(cls, secret):
		results = cls.query(cls.secret == secret).fetch(1)
		return results[0] if len(results) else None

def generate_secret_for_hacker_with_email(email):
	return base64.urlsafe_b64encode(email.encode('utf-8') + ',' + os.urandom(64))

def accept_hacker(hacker):
	deadline = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%m/%d/%y")
	email = template("emails/admitted.html", {"hacker": hacker, "deadline": deadline})
	send_email(recipients=[hacker.email], html=email, subject="We'd like to invite you to Hack@Brown")

	hacker.admitted_email_sent_date = datetime.datetime.now()
	hacker.put()
	memcache.add("admitted:{0}".format(hacker.secret), "1", memcache_expiry)

class RegistrationHandler(blobstore_handlers.BlobstoreUploadHandler):
		def post(self):
			hacker = Hacker()
			hacker.ip = self.request.remote_addr
			for key in hacker_keys:
				vals = self.request.get_all(key)
				val =','.join(vals)
				try:
					setattr(hacker, key, val)
				except datastore_errors.BadValueError as err:
					return self.response.write(json.dumps({"success":False, "msg" : "Register", "field" : str(err.args[0]), "newURL" : blobstore.create_upload_url('/register')}))

			if Hacker.query(Hacker.email == hacker.email).count() > 0:
				return self.response.write(json.dumps({"success":False, "msg": "Email Already Registered!"}))

			resume_files = self.get_uploads('resume')
			if len(resume_files) > 0:
					hacker.resume = resume_files[0].key()
			hacker.secret = generate_secret_for_hacker_with_email(hacker.email)
			try:
				email_html = template("emails/confirm_registration.html", {"name": hacker.name.split(" ")[0], "hacker": hacker})
				send_email(recipients=[hacker.email], subject="You've applied to Hack@Brown!", html=email_html)
				hacker.post_registration_email_sent_date = datetime.datetime.now()
			except Exception, e:
				pass
			hacker.put()
			name = hacker.name.title().split(" ")[0] # TODO: make it better
			confirmation_html = template("post_registration_splash.html", {"name": name, "secret": hacker.secret})
			self.response.write(json.dumps({"success": True, "replace_splash_with_html": confirmation_html}))

class CheckRegistrationHandler(webapp2.RequestHandler):
	def get(self):
		email = self.request.get('email')
		if Hacker.query(Hacker.email == email).count() > 0:
			self.response.write(json.dumps({"registered":True}))
		else:
			#TODO: move this into a more semantic place
			EmailListEntry.add_email(email)
			self.response.write(json.dumps({"registered":False}))


