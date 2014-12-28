import webapp2
from template import template, template_string
from google.appengine.ext import ndb
from send_email import send_email
import re
from google.appengine.api import taskqueue
from registration import Hacker

class Message(ndb.Model):
	added = ndb.DateTimeProperty(auto_now_add=True)
	
	audience = ndb.StringProperty(choices=[None, 'registered', 'invited-friends'], default=None)
	
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
	
	def get_hacker_query(self):
		if self.audience == 'registered':
			return Hacker.query()
		elif self.audience == 'invited-friends':
			return Hacker.query(Hacker.teammates != None)
		else:
			assert 0, "Unknown audience"
	
	def enqueue_tasks(self):
		q = taskqueue.Queue("messages")
		# max task size is 100kb; max # of tasks added per batch is 100
		task_futures = []
		
		batch_size = 40 # 2k users / 40 = 50 tasks. within our limits.
		batch_of_hacker_keys = []
		def send_batch():
			params = {"message_key": self.key.urlsafe(), "hacker_keys": ','.join(batch_of_hacker_keys[:])}
			task = taskqueue.Task(params=params, url='/dashboard/messages/message_task_queue_work')
			task_future = q.add_async(task)
			task_futures.append(task_future)
			batch_of_hacker_keys[:] = []
		
		for key in self.get_hacker_query().iter(keys_only=True):
			batch_of_hacker_keys.append(key.urlsafe())
			if len(batch_of_hacker_keys) >= batch_size: send_batch()
		if len(batch_of_hacker_keys): send_batch()
		
		for f in task_futures:
			f.get_result()
	
	def send_to_hacker(self, hacker):
		if self.audience == 'invited-friends':
			# don't actually send to the hacker -- send to their friends
			if hacker.teammates:
				emails = hacker.teammates.split(',')
				matching_hackers = Hacker.query(Hacker.email.IN(emails)).fetch()
				emails_already_registered = [h.email for h in matching_hackers]
				for email in emails:
					if email not in emails_already_registered:
						self.send_to_email(email, {"invited_by": hacker})
		elif self.audience == 'registered': # send emails directly to hackers
			if hacker.email and self.email_subject:
				self.send_to_email(hacker.email, {"hacker": hacker})
			if hacker.phone_number and self.sms_text:
				self.send_to_phone(self.phone_number)

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
		keys = [ndb.Key(urlsafe=self.request.get('message_key'))] + map(lambda k: ndb.Key(urlsafe=k), self.request.get('hacker_keys').split(','))
		entities = ndb.get_multi(keys)
		message = entities[0]
		hackers = entities[1:]
		for hacker in hackers:
			message.send_to_hacker(hacker)
