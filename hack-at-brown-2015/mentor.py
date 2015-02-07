import webapp2
from template import template
from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
import models
from registration import Hacker
import logging
import json
from google.appengine.api import users
import datetime

maxRating = 5
minRating = 0

def ratingValidator(prop, value):
		if value > maxRating:
				value = maxRating

		if value < minRating:
				value = minRating

class MentorResponse(ndb.Model):
		rating = ndb.IntegerProperty(default=None, validator=ratingValidator)
		request = ndb.KeyProperty(kind='MentorRequest')
		mentor = ndb.KeyProperty(kind='Mentor')
		dispatched = ndb.DateTimeProperty(auto_now_add=True)
		dispatcher = ndb.StringProperty(validator=models.stringValidator)
		finished = ndb.DateTimeProperty()

def formatMentorResponse(mentorResponse):
	mr = mentorResponse.get()
	return {'mentor' : mr.mentor.urlsafe(), 'request' : mr.request.urlsafe(), 'id' : mr.key.urlsafe()}

#Anyone who will give help to a hacker.
class Mentor(ndb.Model):
		phone = ndb.StringProperty(validator=models.phoneValidator, default=None)
		email = ndb.StringProperty(validator=models.stringValidator, default=None)
		name = ndb.StringProperty()
		tags = ndb.StringProperty(validator=models.stringValidator, repeated=True)
		role = ndb.TextProperty() # e.g. Oracle Engineer
		availability = ndb.TextProperty()
		details = ndb.TextProperty()
		responded = ndb.KeyProperty(kind=MentorResponse, repeated=True)
		#perhaps should be key property
		assigned = ndb.BooleanProperty(default=False)

		def getResponded(self):
				return [key.get() for key in self.responded]

		def computeAvg(self):
				responded = self.getResponded()
				ratedResponded = [x for x in responded if x.rating]

				if len(ratedResponded) == 0:
					return 3
				else:
					return (reduce(lambda x, y: x + y.rating, ratedResponded, 0) / len(ratedResponded))

		def asDict(self, include_keys):
			return {key: getattr(self, key, None) for key in include_keys}

def formatMentor(mentor):
	md = mentor.asDict(Mentor._properties)
	md['responded'] = len(mentor.responded)
	md['id'] = mentor.key.urlsafe()
	md['rating'] = mentor.computeAvg()
	return md

class MentorRequest(ndb.Model):
	requester = ndb.KeyProperty(default=None)
	requester_phone = ndb.StringProperty(default=None, validator=models.stringValidator)
	location = ndb.StringProperty(default=None)
	created = ndb.DateTimeProperty(auto_now_add=True)
	responses = ndb.KeyProperty(kind=MentorResponse, repeated=True)
	issue = ndb.TextProperty(required=False)
	tags = ndb.StringProperty(repeated=True)
	status = ndb.StringProperty(choices=['solved', 'assigned', 'unassigned'], default='unassigned')
	def asDict(self, include_keys):
		d = {key: getattr(self, key, None) for key in include_keys}
		return d

def formatRequest(mentorRequest):
	mr =  mentorRequest.asDict(['location', 'created', 'issue', 'tags', 'status'])
	mr['created'] = pretty_date(mentorRequest.created)
	mr['id'] = mentorRequest.key.urlsafe()
	mr['responses'] = len(mentorRequest.responses)
	mr['requester_phone'] = mentorRequest.requester_phone
	mr['requester_name'] = mentorRequest.requester.get().name if mentorRequest.requester else None
	return mr


class MentorRequestHandler(webapp2.RequestHandler):
		def get(self):
				self.response.write(template('mentor_request.html', {}))

		def post(self):
				hackers = Hacker.query(Hacker.phone_number == self.request.get('phone')).fetch(keys_only=True)

				request = MentorRequest()
				request.location = self.request.get('location')
				request.issue = self.request.get('issue')
				request.tags = self.request.get('tags').split(', ')
				if len(hackers):
					request.requester = hackers[0]
				request.requester_phone = self.request.get('phone')
				request.put()

				self.redirect('/?dayof=1#mrc') # #mrc: mentor-request-confirm (we don't want that showing up in URLs)

class MentorSignupHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write(template("mentor_signup.html"))
	def post(self):
		keys = ['name', 'role', 'email', 'phone', 'availability', 'tags', 'details']
		try:
			mentor = Mentor()
			for key in keys:
				val = self.request.get(key)
				if key == 'tags':
					val = [tag.strip().lower() for tag in val.split(',')]
				setattr(mentor, key, val)
			mentor.put()
			first_name = mentor.name.split(' ')[0] if mentor.name else 'mentor'
			self.response.write(template("mentor_signup.html", {"show_confirmation": True, "first_name": first_name}))
		except datastore_errors.BadValueError as e:
			print "MENTOR SIGNUP ERROR: {0}".format(e)
			self.response.write(template("mentor_signup.html", {"error": "There's an invalid or missing field on your form!"}))
			self.response.write(template("mentor_dispatch.html"))

class DispatchHandler(webapp2.RequestHandler):
		def get(self):
			self.response.write(template("mentor_dispatch.html"))

		def post(self):
			data = json.loads(self.request.body)
			request = ndb.Key(urlsafe=data['request']).get()
			mentor  = ndb.Key(urlsafe=data['mentor']).get()

			response = MentorResponse()
			response.dispatcher = users.get_current_user().email()
			response.mentor = mentor.key
			response.request = request.key
			response.put()

			mentor.responded.append(response.key)
			mentor.assigned = True
			request.responses.append(response.key)
			request.status='assigned'

			request.put()
			mentor.put()

			return self.response.write(json.dumps({'success' : True}))

class ResponseFinishedHandler(webapp2.RequestHandler):
	def post(self):
		data = json.loads(self.request.body)

		response = ndb.Key(urlsafe=data['id']).get()
		mentor = response.mentor.get()
		request = response.request.get()

		if data.get('rating'):
			response.rating = int(data.get('rating'))

		request.status = data['status'] #could be completed or unassigned
		response.finished = datetime.datetime.now()
		mentor.assigned = False

		response.put()
		mentor.put()
		request.put()
		return self.response.write(json.dumps({'success' : True}))


class GetRequestsHandler(webapp2.RequestHandler):
	def get(self):

		requests = map(formatRequest, MentorRequest.query(MentorRequest.status == 'unassigned').order(MentorRequest.created).fetch())
		return self.response.write(json.dumps({'requests' : requests}))

class GetAssignedHandler(webapp2.RequestHandler):
	def get(self):
		mentors = Mentor.query(Mentor.assigned == True).fetch()
		mentors = map(formatMentor, mentors)

		requests = MentorRequest.query(MentorRequest.status == 'assigned').fetch()

		pairs =  [r.responses[-1] for r in requests if len(r.responses) > 0]
		pairs = map(formatMentorResponse, pairs)

		requests = map(formatRequest, requests)


		self.response.write(json.dumps({'assigned_mentors' : mentors, 'assigned_requests' : requests, 'pairs' : pairs}))


class ViewRequestHandler(webapp2.RequestHandler):
	def get(self, id):
		request = ndb.Key(urlsafe=id).get()

		mentors = map(formatMentor, findMentorsForRequest(request))
		return self.response.write(json.dumps({'request' : formatRequest(request), 'mentors' : mentors}))

def findMentorsForRequest(request):
	tags = [t.lower() for t in request.tags]
	mentors = Mentor.query(Mentor.assigned == False).fetch()
	# Each mentor should be assessed based on:
	# 1. # of tags matching that of request
	# 2. # of previously completed tasks balanced with rating
	# should return list of best mentors
	#First sort by responded.
	mentors.sort(key=lambda m: len(m.responded))
	#Then sort by rating
	mentors.sort(key=lambda m: m.computeAvg(), reverse=True)
	#Finally sort by relevance of tags
	mentors.sort(key=lambda m: len([t for t in m.tags if t.lower() in request.tags]), reverse=True)
	return mentors

def pretty_date(time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""
	now = datetime.datetime.now()
	if type(time) is int:
		diff = now - datetime.datetime.fromtimestamp(time)
	elif isinstance(time,datetime.datetime):
		diff = now - time
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return "a minute ago"
		if second_diff < 3600:
			return str(second_diff / 60) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str(second_diff / 3600) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff / 7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff / 30) + " months ago"
	return str(day_diff / 365) + " years ago"


