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

#Anyone who will give help to a hacker.
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
    issue = ndb.TextProperty(required=False)
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

# These should sum to 1
mweight_tags    = 0.6
mweight_rating  = 0.25
mweight_numdone = 0.15

def findMentorsForRequest(request):
    tags = [t.lowercase for t in request.tags]
    all_mentors = Mentor.query().fetch()
    # Each mentor should be assessed based on:
    # 1. # of tags matching that of request
    # 2. # of previously completed tasks balanced with rating
    # should return list of best mentors
    tagmap = {m:[request.tags.contains(t.lowercase) for t in tags].len for m in all_mentors}
    appropriate_mentors = [(k,v) for (k,v) in tagmap.iteritems() if v > 0]
    appropriate_mentors.sort(lambda x: 
        ((x[1]/len(request.tags) * mweight_tags) + (x[0].computeAvg()/maxRating * mweight_rating) + (1/(len(x[0].getResponded())+1) * mweight_numdone)), 
        reverse=True)
    return appropriate_mentors




