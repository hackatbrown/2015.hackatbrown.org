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

class Message(ndb.Model):
	added = ndb.DateTimeProperty(auto_now_add=True)
	
	audience = ndb.StringProperty(choices=[None, 'registered', 'invited-friends', 'mailing-list-unregistered'], default=None)
	
	email_subject = ndb.TextProperty()
	email_html = ndb.TextProperty()
	
	sms_text = ndb.TextProperty()
	
	def send_to_email(self, email, template_args={}):
		# does the actual work of sending
		assert self.email_subject, "No email subject provided. Is email unchecked?"
		html = template_string(self.email_html, template_args)
		html = template("emails/generic.html", dict({"content": html}.items() + template_args.items()))
		subject = template_string(self.email_subject, template_args)
		send_email(html, subject, [email])
	
	def send_to_phone(self, phone):
		# actual work of sms'ing
		print "SHOULD SEND SMS '{0}' TO {1}, but not yet implemented".format(self.sms_text, phone)
	
	def get_query(self):
		if self.audience == 'registered':
			return Hacker.query()
		elif self.audience == 'invited-friends':
			return Hacker.query(Hacker.teammates != None)
		elif self.audience == 'mailing-list-unregistered':
			return EmailListEntry.query()
		else:
			assert 0, "Unknown audience"
	
	def enqueue_tasks(self):
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
				self.send_to_phone(self.phone_number)
		elif self.audience == 'mailing-list-unregistered':
			email = entity.email
			is_registered = (yield Hacker.query(Hacker.email == email).count_async()) > 0
			if not is_registered:
				self.send_to_email(email, {})

class MessagesDashboardHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write(template("messages_dashboard.html", {}))
	
	def post(self):
		message = Message(audience=self.request.get('audience'))
		if self.request.get('email'):
			message.email_subject = self.request.get('email-subject')
			message.email_html = self.request.get('email-html')
		if self.request.get('sms'):
			message.sms_text = self.request.get('sms-text')
		
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
			message.enqueue_tasks()
			self.response.write(template("messages_dashboard.html", {"status": "Sent!"}))

class MessagesTaskQueueWork(webapp2.RequestHandler):
	def post(self):
		keys = [ndb.Key(urlsafe=self.request.get('message_key'))] + map(lambda k: ndb.Key(urlsafe=k), self.request.get('entity_keys').split(','))
		msg_and_entities = ndb.get_multi(keys)
		message = msg_and_entities[0]
		entities = msg_and_entities[1:]
		futures = [message.send_to_entity_async(entity) for entity in entities]
		for f in futures: f.wait()
