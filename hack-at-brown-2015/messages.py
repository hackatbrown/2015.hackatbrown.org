"""
HOW THIS WORKS:
1. Message objects are created via /dashboard/messages. Message objects have a string indicating their audience (e.g. all registered hackers, all checked-in, mailing list people, teammates listed on people's applications)
2. Message.enqueue_tasks() enqueues a bunch of Tas objects in the `messages` queue, by:
 2.1 calling Message.get_query() to get a datastore query
 2.2 batching the entities returned from the query into groups of 40 (batch_size)
 2.3 creating Task Queue tasks for each batch, containing message ID and entity ID for all entities
3. MessagesTaskQueueWork.post is called by the task queue for each task.
4. MessagesTaskQueueWork.post loads the Message object and all entities, then concurrently calls Message.send_to_entity_async(entity) on each entity. These are responsible for looking the audience, the current entity (which may be a Hacker or an EmailListEntry, or maybe something else in the future), and sending the appropriate emails or SMSs
"""

import webapp2
from template import template, template_string
from google.appengine.ext import ndb
from send_email import send_email
import re
from google.appengine.api import taskqueue
from registration import Hacker
from email_list import EmailListEntry
import sms
from config import isAdmin
import datetime

class Message(ndb.Model):
	added = ndb.DateTimeProperty(auto_now_add=True)

	audience = ndb.StringProperty(choices=[None, 'registered', 'invited-friends', 'mailing-list-unregistered', 'waitlisted', 'accepted-highschool-freshmen','hardware-hackers', 'accepted', 'accepted-non-local', 'accepted-local', 'checked-in', 'rsvped-first-time', 'local-waitlisted'], default=None)

	email_from_template = ndb.BooleanProperty(default=False)
	email_subject = ndb.TextProperty()
	email_html = ndb.TextProperty()

	sms_text = ndb.TextProperty()
	
	show_in_day_of = ndb.BooleanProperty()
	day_of_html = ndb.TextProperty()

	def kick_off(self):
		q = taskqueue.Queue("messages")
		q.add(taskqueue.Task(url='/dashboard/messages/message_task_queue_work', params={"kickoff_message_key": self.key.urlsafe()}))

	def send_to_email(self, email, template_args={}):
		# does the actual work of sending
		emails = [email]
		assert self.email_subject, "No email subject provided. Is email unchecked?"
		if self.email_from_template:
			html = template("emails/" + self.email_html + ".html", template_args)
		else:
			html = template_string(self.email_html, template_args)
			html = template("emails/generic.html", dict({"content": html}.items() + template_args.items()))
		subject = template_string(self.email_subject, template_args)
		send_email(html, subject, emails)

	def send_to_phone(self, phone):
		# actual work of sms'ing
		print "Sending SMS '{0}' to {1}".format(self.sms_text, phone)
		sms.send(phone, self.sms_text)

	def get_query(self):
		if self.audience == 'registered':
			return Hacker.query()
		elif self.audience == 'accepted':
			return Hacker.query(Hacker.admitted_email_sent_date != None)
		elif self.audience == 'accepted-non-local':
			return Hacker.query(Hacker.admitted_email_sent_date != None)
		elif self.audience == 'invited-friends':
			return Hacker.query(Hacker.teammates != None)
		elif self.audience == 'mailing-list-unregistered':
			return EmailListEntry.query()
		elif self.audience == 'waitlisted':
			print "sending waitlisted emails: " + str(Hacker.query(Hacker.admitted_email_sent_date == None).count())
			return Hacker.query(Hacker.admitted_email_sent_date == None)
		elif self.audience == 'hardware-hackers':
			print "sending emails to admitted hardware-hackers: " +  str(Hacker.query(Hacker.admitted_email_sent_date != None, Hacker.hardware_hack == 'yes').count())
			return Hacker.query(Hacker.admitted_email_sent_date != None, Hacker.hardware_hack == 'yes')
		elif self.audience == 'accepted-highschool-freshmen':
			print "sending emails to accepted highschool and freshman hackers"
			return Hacker.query(ndb.AND(Hacker.admitted_email_sent_date != None, ndb.OR(Hacker.year == 'highschool', Hacker.year == 'freshman')))
		elif self.audience == 'local-waitlisted':
			print "sending emails to local waitlisted hackers: "
			return Hacker.query(Hacker.admitted_email_sent_date == None)
		elif self.audience == 'rsvped-first-time':
			print "sending emails to rsvped-first-time hackers"
			return Hacker.query(ndb.AND(Hacker.rsvpd == True, Hacker.first_hackathon =='yes'))
		elif self.audience == 'checked-in':
			print 'sending emails to checked-in hackers: ' + str(Hacker.query(Hacker.checked_in == True).count())
			return Hacker.query(Hacker.checked_in == True)
		elif self.audience == 'accepted-local':
			print "sending emails to accepted-local"
			return Hacker.query(Hacker.admitted_email_sent_date != None)
		elif self.audience == None:
			return None
		else:
			assert 0, "Unknown audience"

	def enqueue_tasks(self):
		if self.get_query() == None:
			print "No audience selected. No emails sent through messages system."
			return
		q = taskqueue.Queue("messages")
		# max task size is 100kb; max # of tasks added per batch is 100
		task_futures = []

		batch_size = 40 # 2k users / 40 = 50 tasks. within our limits.
		batch_of_entity_keys = []
		def send_batch():
			params = {"message_key": self.key.urlsafe(), "entity_keys": ','.join(batch_of_entity_keys[:])}
			task = taskqueue.Task(params=params, url='/dashboard/messages/message_task_queue_work')
			task_future = q.add_async(task)
			task_futures.append(task_future)
			batch_of_entity_keys[:] = []

		for key in self.get_query().iter(keys_only=True):
			batch_of_entity_keys.append(key.urlsafe())
			if len(batch_of_entity_keys) >= batch_size: send_batch()
		if len(batch_of_entity_keys): send_batch()

		for f in task_futures:
			f.get_result()

	@ndb.tasklet
	def send_to_entity_async(self, entity):
		try:
			if self.audience == 'invited-friends':
				# don't actually send to the hacker -- send to their friends
				hacker = entity
				if hacker.teammates:
					emails = [email.lower() for email in hacker.teammates.split(',')]
					matching_hackers = yield Hacker.query(Hacker.email.IN(emails)).fetch_async()
					emails_already_registered = [h.email for h in matching_hackers]
					for email in emails:
						if email not in emails_already_registered:
							self.send_to_email(email, {"invited_by": hacker})
			elif self.audience == 'registered': # send emails directly to hackers
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'mailing-list-unregistered':
				email = entity.email
				is_registered = (yield Hacker.query(Hacker.email == email).count_async()) > 0
				if not is_registered:
					self.send_to_email(email, {})
			elif self.audience == 'waitlisted':
				hacker = entity
				hacker.waitlist_email_sent_date = datetime.datetime.now()
				self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				hacker.put()
			elif self.audience == 'hardware-hackers': #also send directly to hackers
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'accepted':
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'accepted-non-local':
				hacker = entity
				if hacker.school == "Brown University" or hacker.school == "Rhode Island School of Design":
					return
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:	
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'local-waitlisted':
				hacker = entity
				print hacker.school
				if hacker.school != "Brown University" and hacker.school != "Rhode Island School of Design":
					return
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'accepted-highschool-freshmen':
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'rsvped-first-time':
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'checked-in':
				hacker = entity
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)
			elif self.audience == 'accepted-local':
				hacker = entity
				print hacker.school
				if hacker.school != "Brown University" and hacker.school != "Rhode Island School of Design":
					return
				if hacker.email and self.email_subject:
					self.send_to_email(hacker.email, {"hacker": hacker, "name":hacker.name.split(" ")[0]})
				if hacker.phone_number and self.sms_text:
					self.send_to_phone(hacker.phone_number)

		except Exception as e:
			print "Failed to send email '{0}' to '{1} because {2}'".format(self.email_subject, entity.email, e)

class MessagesDashboardHandler(webapp2.RequestHandler):
	def get(self):
		if not isAdmin(): return self.redirect('/')
		self.response.write(template("messages_dashboard.html", {}))

	def post(self):
		if not isAdmin(): return self.redirect('/')
		audience = None if self.request.get('audience') == '' else self.request.get('audience')
		message = Message(audience=audience)
		if self.request.get('email'):
			message.email_subject = self.request.get('email-subject')
			if self.request.get('email-name'):
				message.email_from_template = True
				message.email_html = self.request.get('email-name')
			else:
				message.email_html = self.request.get('email-html')
		if self.request.get('sms'):
			message.sms_text = self.request.get('sms-text')
		if self.request.get('show-in-day-of'):
			message.day_of_html = self.request.get('day-of-html')
			message.show_in_day_of = True
		if self.request.get('test'):
			recip = self.request.get('test-recipient')
			if '@' in recip:
				message.send_to_email(recip)
				self.response.write("Sent email")
			elif len(recip) > 0:
				message.send_to_phone(recip)
				self.response.write("Sent SMS")
		else:
			message.put()
			message.kick_off()
			self.response.write(template("messages_dashboard.html", {"status": "Sent!"}))

class MessagesTaskQueueWork(webapp2.RequestHandler):
	def post(self):
		#if not isAdmin(): return self.redirect('/')
		if self.request.get('kickoff_message_key'):
			ndb.Key(urlsafe=self.request.get('kickoff_message_key')).get().enqueue_tasks()
		elif self.request.get('entity_keys'):
			keys = [ndb.Key(urlsafe=self.request.get('message_key'))] + map(lambda k: ndb.Key(urlsafe=k), self.request.get('entity_keys').split(','))
			msg_and_entities = ndb.get_multi(keys)
			message = msg_and_entities[0]
			entities = msg_and_entities[1:]
			futures = [message.send_to_entity_async(entity) for entity in entities]
			for f in futures: f.wait()
