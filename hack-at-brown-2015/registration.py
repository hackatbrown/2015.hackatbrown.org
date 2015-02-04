
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
from config import admission_expiration_seconds
import deletedHacker
import models


memcache_expiry = 10 * 60
hacker_keys = ['name', 'school', 'year', 'email', 'shirt_size', 'shirt_gen', 'dietary_restrictions', 'teammates', 'hardware_hack', 'links', 'first_hackathon']
personal_info_keys = ['name', 'email', 'teammates', 'links']

class Hacker(ndb.Model):
	#TODO: If you add a new property, please remember to add that property to deletedHacker.py.

	name = ndb.StringProperty(validator=models.stringValidator)
	school = ndb.StringProperty(validator=models.stringValidator)
	year = ndb.StringProperty(choices=['highschool', 'freshman', 'sophomore', 'junior', 'senior', 'grad_student'])
	email = ndb.StringProperty(validator=models.stringValidator)
	shirt_gen = ndb.StringProperty(choices=['M', 'W'])
	shirt_size = ndb.StringProperty(choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])
	dietary_restrictions = ndb.StringProperty(validator=models.stringValidator)
	resume = ndb.BlobKeyProperty()
	receipts = ndb.BlobKeyProperty(repeated=True)
	date = ndb.DateTimeProperty(auto_now_add=True)
	links = ndb.StringProperty(default=None)
	teammates = ndb.StringProperty(default=None, validator=models.stringValidator)
	teammates_emailed = ndb.BooleanProperty(default=False)
	hardware_hack = ndb.StringProperty(choices=["yes", 'no'])
	first_hackathon = ndb.StringProperty(choices=['yes', 'no'])


	phone_number = ndb.StringProperty(validator=models.phoneValidator) # normalized to only digits, no country code
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
	rsvp_reminder_sent_date = ndb.DateTimeProperty(default=None)

	rsvpd = ndb.BooleanProperty(default=False)
	checked_in = ndb.BooleanProperty(default=False)
	deadline = ndb.DateTimeProperty()

	ip = ndb.StringProperty()

	#Only collected for reimbursements.
	address1 = ndb.StringProperty()
	address2 = ndb.StringProperty()
	city = ndb.StringProperty()
	state = ndb.StringProperty()
	zip = ndb.StringProperty()
	country =ndb.StringProperty()

	rmax = ndb.IntegerProperty(default = 0)
	rtotal = ndb.IntegerProperty(default = 0)

	def computeStatus(self):
			if self is None:
					return "not found"
			if self.checked_in == True:
					return "checked in"
			elif self.rsvpd == True:
					return "confirmed"
			elif self.admitted_email_sent_date != None:
					return "accepted"
			elif self.waitlist_email_sent_date != None:
					return "waitlisted"
			else:
					return "pending"

	def asDict(self, include_keys):
			d = {key: getattr(self, key, None) for key in include_keys}
			if 'status' in include_keys:
				d['status'] = self.computeStatus()
			if 'has_resume' in include_keys:
				d['has_resume'] = False if (not hasattr(self, 'resume') or self.resume == {} or self.resume ==	None) else True
			return d

	@classmethod
	def WithSecret(cls, secret):
		results = cls.query(cls.secret == secret).fetch(1)
		return results[0] if len(results) else None



def generate_secret_for_hacker_with_email(email):
	return base64.urlsafe_b64encode(email.encode('utf-8') + ',' + os.urandom(64))

def accept_hacker(hacker):
	#print "actually accepting hacker"
	hacker.deadline = (datetime.datetime.now() + datetime.timedelta(seconds=admission_expiration_seconds()))
	if hacker.deadline > datetime.datetime(2015, 2, 7):
		hacker.deadline = datetime.datetime(2015, 2, 7)
	email = template("emails/admitted.html", {"hacker": hacker, "deadline": hacker.deadline.strftime("%m/%d/%y"), "name":hacker.name.split(" ")[0]})
	send_email(recipients=[hacker.email], html=email, subject="You got off the Waitlist for Hack@Brown!")

	hacker.admitted_email_sent_date = datetime.datetime.now()
	hacker.put()
	memcache.add("admitted:{0}".format(hacker.secret), "1", memcache_expiry)

def create_hacker(dict):
	hacker = Hacker()
	for key, value in dict.items():
		setattr(hacker, key, value)

	if not hacker.email:
		return False

	hacker.secret = generate_secret_for_hacker_with_email(hacker.email)
	try:
		accept_hacker(hacker)
		return True
	except datastore_errors.BadValueError:
		return False

def expire_hacker(hacker):
	if hacker.rsvpd == True or hacker.admitted_email_sent_date == None:
			#hacker has rsvp'd or was never accepted
			return
	print "Expiring " + hacker.email + " with admit date: " + str(hacker.admitted_email_sent_date)
	email = template("emails/admittance_expired.html", {"name":hacker.name.split(" ")[0]})
	send_email(recipients=[hacker.email], html=email, subject="You didn't RSVP to Hack@Brown in time...")
	deletedHacker.createDeletedHacker(hacker, "expired")
	hacker.key.delete()

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
			# try:
			#		email_html = template("emails/confirm_registration.html", {"name": hacker.name.split(" ")[0], "hacker": hacker})
			#		send_email(recipients=[hacker.email], subject="You've applied to Hack@Brown!", html=email_html)
			#		hacker.post_registration_email_sent_date = datetime.datetime.now()
			# except Exception, e:
			#		pass
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




