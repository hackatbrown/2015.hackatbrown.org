maxRating = 5
minRating = 0

def ratingValidator(prop, value):
    if value > maxRating:
        value = maxRating

    if value < minRating:
        value = minRating

class Mentor(ndb.Model):
    phone = ndb.StringProperty(validator=phoneValidator)
    email = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    responses = MentorRequestKey(repeated=True)
    ratings = ndb.IntegerProperty(repeated=True, validator=ratingValidator)
    avg = ndb.computedProperty(reduce(+, ratings) / self.responses.length)

class MentorRequest(ndb.Model):
    hacker = Hacker.key(required=True)
    location = ndb.StringProperty(required=True)
    sent = ndb.DateTimeProperty(auto_now_add=True)
    responded = ndb.StructuredProperty(repeated=True)
    #Time / Mentor / DispatcherEmail
    issue = ndb.TextProperty(required=True)
    tags = ndb.StringProperty(repeated=True)

