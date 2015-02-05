import webapp2
from template import template
from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
import models
from registration import Hacker

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

class Mentor(ndb.Model):
    phone = ndb.StringProperty(validator=models.phoneValidator, default=None)
    email = ndb.StringProperty(validator=models.stringValidator, default=None)
    tags = ndb.StringProperty(validator=models.stringValidator, repeated=True)
    responded = ndb.KeyProperty(kind=MentorResponse, repeated=True)

    def getResponded(self):
        return [key.get() for key in self.responded]

    def computeAvg(self):
        ratedResponded = [x for x in self.getResponded() if x.rating]
        return (reduce(lambda x, y: x.rating + y, ratedResponded) / len(ratedResponded))

class MentorRequest(ndb.Model):
    requester = ndb.KeyProperty(default=None)
    location = ndb.StringProperty(default=None)
    created = ndb.DateTimeProperty(auto_now_add=True)
    responses = ndb.KeyProperty(kind=MentorResponse, repeated=True)
    issue = ndb.TextProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    status = ndb.StringProperty(choices=['solved', 'assigned', 'unassigned'], default='unassigned')

class MentorRequestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template('mentor_request.html', {}))

    def post(self):
        hacker = Hacker.query(Hacker.email == self.request.get('email')).fetch(keys_only=True)
        if hacker is None:
            return self.response.write('failure')

        request = MentorRequest()
        request.location = self.request.get('location')
        request.issue = self.request.get('issue')
        request.tags = self.request.get('tags').split(', ')
        request.put()

        return self.response.write('success')

class DispatchHandler(webapp2.RequestHandler):
    def get(self):
        #TODO: clicking a request should load the issue in centered
        #      and populate the mentor list. Clicking a mentor in
        #      should bring up that mentor's contact info and all
        #      skills. Another click should assign that mentor.
        #TODO: sort requests by created, #responses.
        #TODO: sort mentors by tags match, #responded, rating
        #TODO: color code mentors by Sponsor/Hacker/Volunteer
        #TODO: mentor cards need tags, number responses.

        self.response.write(template("mentor_dispatch.html"))
