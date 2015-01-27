from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
import models

maxRating = 5
minRating = 0

def ratingValidator(prop, value):
    if value > maxRating:
        value = maxRating

    if value < minRating:
        value = minRating

def MentorResponse(ndb.Model):
    rating = ndb.IntegerProperty(default=None, validator=ratingValidator):
    request = ndb.KeyProperty(kind=MentorRequest)
    mentor = ndb.KeyProperty(kind=Mentor)
    dispatched = ndb.DateTimeProperty(auto_now_add=True)
    dispatcher = ndb.StringProperty(validator=models.stringValidator)
    finished == ndb.DateTimeProperty()

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
    requested = ndb.KeyPropery(default=None)
    location = ndb.StringProperty(default=None)
    sent = ndb.DateTimeProperty(auto_now_add=True)
    responses = ndb.KeyProperty(kind=MentorResponse, repeated=True)
    issue = ndb.TextProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    solved = ndb.BooleanProperty(default=False)
