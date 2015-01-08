from google.appengine.ext import ndb
from registration import Hacker

class DeletedHacker(ndb.Model):
    name = ndb.StringProperty()
    school = ndb.StringProperty()
    year = ndb.StringProperty()

    email = ndb.StringProperty()
    shirt_gen = ndb.StringProperty()
    shirt_size = ndb.StringProperty()

    dietary_restrictions = ndb.StringProperty()
    resume = ndb.BlobKeyProperty()
    date = ndb.DateTimeProperty()

    links = ndb.StringProperty()
    teammates = ndb.StringProperty()
    teammates_emailed = ndb.BooleanProperty()

    hardware_hack = ndb.StringProperty()
    first_hackathon = ndb.StringProperty()
    phone_number = ndb.StringProperty() # normalized to only digits, plz


    secret = ndb.StringProperty()
    admit_priority = ndb.FloatProperty(default=0)
    admitted_email_sent_date = ndb.DateTimeProperty()

    post_registration_email_sent_date = ndb.DateTimeProperty()
    waitlist_email_sent_date = ndb.DateTimeProperty()
    rsvpd = ndb.BooleanProperty()

    checked_in = ndb.BooleanProperty()
    ip = ndb.StringProperty()

    receipts = ndb.BlobKeyProperty(repeated=True)
    #different
    deletedDate = ndb.DateTimeProperty(auto_now_add=True)
    deletedCause = ndb.StringProperty(choices=["unregistered", "expired"])

def createDeletedHacker(hacker, cause):
    deletedHacker = DeletedHacker()

    deletedHacker.name = hacker.name
    deletedHacker.school = hacker.school
    deletedHacker.year = hacker.year

    deletedHacker.shirt_gen = hacker.shirt_gen
    deletedHacker.shirt_size = hacker.shirt_size
    deletedHacker.dietary_restrictions = hacker.dietary_restrictions

    deletedHacker.resume = hacker.resume
    deletedHacker.date = hacker.date
    deletedHacker.links = hacker.links

    deletedHacker.teammates = hacker.teammates
    deletedHacker.teammates_emailed = hacker.teammates_emailed
    deletedHacker.hardware_hack = hacker.hardware_hack

    deletedHacker.first_hackathon = hacker.first_hackathon
    deletedHacker.phone_number = hacker.phone_number
    deletedHacker.secret = hacker.secret

    deletedHacker.admit_priority = hacker.admit_priority
    deletedHacker.admitted_email_sent_date = hacker.admitted_email_sent_date
    deletedHacker.post_registration_email_sent_date = hacker.post_registration_email_sent_date

    deletedHacker.waitlist_email_sent_date = hacker.waitlist_email_sent_date
    deletedHacker.rsvpd = hacker.rsvpd
    deletedHacker.checked_in = hacker.checked_in

    deletedHacker.ip = hacker.ip

    deletedHacker.receipts = hacker.receipts
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zip = ndb.StringProperty()
    country =ndb.StringProperty()

    rmax = ndb.IntegerProperty(default = 0)
    rtotal = ndb.IntegerProperty(default = 0)


    deletedHacker.deletedCause = cause
    deletedHacker.put()
