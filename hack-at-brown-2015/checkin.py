import logging
import webapp2
import json
from template import template
from registration import Hacker
from registration import hacker_keys
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import channel
from google.appengine.api import users
from config import onTeam
import hacker_page
import datetime

cacheTime = 6 * 10

class CheckInSession(ndb.Model):
    total = ndb.IntegerProperty(default=0)

class CheckinPageHandler(webapp2.RequestHandler):

    def get(self):
        if not onTeam(): return self.redirect('/')

        user = users.get_current_user()
        if not user:
          self.redirect(users.create_login_url(self.request.uri))
          return

        def formatter(person):
            JSON = {}
            key = getattr(person, 'key')
            JSON['id'] = key.urlsafe()
            JSON['kind'] = key.kind()
            JSON.update(person.asDict(['email', 'name', 'checked_in']))
            return JSON

        source = map(formatter, Hacker.query().fetch())

        #TODO: Remove this Test Data
        source += [{'id': 1, 'kind': 'Volunteer', 'email': 'samuel_kortchmar@brown.edu', 'name': 'Samuel Kortchmar'}, {'id': 2, 'kind': 'Company Rep', 'email': 'hats@brown.edu', 'name': 'Sponsor Sponsor'}]

        session = CheckInSession()
        session.put()
        token = channel.create_channel(session.key.urlsafe())

        self.response.write(template("checkin.html", {"source" : json.dumps(source), 'total_checked_in' : Hacker.query(Hacker.checked_in == True).count(), 'token' : token}))

    def post(self):
        if not onTeam(): return self.response.write({'success' : False, 'message' : 'You do not have permission to do this'})

        id = json.loads(self.request.body).get('id')
        hacker = ndb.Key(urlsafe=id).get()

        if hacker is None:
            success = False
            newTotal = 0
        else:
            newTotal = Hacker.query(Hacker.checked_in == True).count() + 1
            #We do this before so eventual consistency doesn't confuse users
            success = True
            hacker.checked_in = True
            hacker.put()

        for session in CheckInSession.query():
            channel.send_message(session.key.urlsafe(), str(newTotal))

        msg = "{0} in hacker {1} - {2}".format('successfully checked' if success else 'failed to check', hacker.name, hacker.email)

        self.response.write(json.dumps({'success' : success, 'message' : msg, 'total_checked_in' : newTotal}))

class MoreInfoHandler(webapp2.RequestHandler):
    def get(self, id):
        infoKeys = hacker_keys + ['checked_in']

        hacker = ndb.Key(urlsafe=id).get()
        hackerDict = hacker.asDict(infoKeys)
        hackerDict.update({'id' : id})

        optionalKeys = ['phone_number', 'resume']
        missingOptional = [key for key in optionalKeys if not getattr(hacker, key, None)]

        required = {}
        # if hacker.year == "highschool":
        required.update({'Parental Waiver' : 'Confirm this hacker is 18 or has a waiver.'})

        defaultReminders = ['Remind this hacker about food or something.', 'Remind this hacker that travel receipts are due on 1.2.2015']

        self.response.write(json.dumps({'hacker': hackerDict, 'missingOptionalInfo' : missingOptional, 'requiredInfo' : required, 'reminders' : defaultReminders}))


class CreateNewPersonHandler(webapp2.RequestHandler):
    def post(self):
        logging.info(self.request.body)
        self.response.write('success')


def getHackersToBeChecked():
    # Cache this value, results don't need to be updated quickly.
    toCheckIn = 'hackers_to_be_checked'
    data = memcache.get(toCheckIn)
    if data is not None:
        logging.debug("Used cache")
        return data
    else:
        data = Hacker.query(ndb.AND(Hacker.rsvpd == True, Hacker.checked_in != True)).fetch(projection=[Hacker.name, Hacker.email])
        logging.debug("Could not use cache")
        if not memcache.add(toCheckIn, data, cacheTime):
            logging.error('Memcache set failed')
    return data

class DeleteSessionHandler(webapp2.RequestHandler):
    #TOOD: - should all be memcached
    def post(self):
        client_id = self.request.get('from')
        if client_id is not None:
            ndb.Key(urlsafe=client_id).delete()

app = webapp2.WSGIApplication([
    ('/checkin', CheckinPageHandler),
    ('/checkin/new', CreateNewPersonHandler),
    ('/checkin/info/(.+)', MoreInfoHandler),
    ('/_ah/channel/disconnected/', DeleteSessionHandler)
], debug=True)
