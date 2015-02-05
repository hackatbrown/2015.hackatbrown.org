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
import registration
import datetime
import models
from google.appengine.api import datastore_errors

cacheTime = 6 * 10

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

        from models import Volunteer, Rep

        source = map(formatter, Hacker.query(Hacker.checked_in == False).fetch())
        source += map(formatter, Rep.query(Rep.checked_in == False).fetch())
        source += map(formatter, Volunteer.query(Volunteer.checked_in == False).fetch())

        total_checked_in = getTotal()

        #TODO: Remove this Test Data
        # source += [{'id': 1, 'kind': 'Volunteer', 'email': 'samuel_kortchmar@brown.edu', 'name': 'Samuel Kortchmar'}, {'id': 2, 'kind': 'Company Rep', 'email': 'hats@brown.edu', 'name': 'Sponsor Sponsor'}]

        session = models.CheckInSession()
        session.user = user.email()

        session.put()
        token = channel.create_channel(session.key.urlsafe())

        self.response.write(template("checkin.html", {"source" : json.dumps(source), 'total_checked_in' : total_checked_in, 'token' : token}))

    def post(self):
        if not onTeam(): return self.response.write({'success' : False, 'message' : 'You do not have permission to do this'})

        id = json.loads(self.request.body).get('id')
        hacker = ndb.Key(urlsafe=id).get()

        if hacker is None:
            success = False
            newTotal = 0
        else:
            newTotal = getTotal(increment_first=True)
            #We do this before so eventual consistency doesn't confuse users
            success = True
            hacker.checked_in = True
            hacker.put()

        for session in models.CheckInSession.query(models.CheckInSession.active == True):
            channel.send_message(session.key.urlsafe(), str(newTotal))

        msg = "{0} in hacker {1} - {2}".format('successfully checked' if success else 'failed to check', hacker.name, hacker.email)

        self.response.write(json.dumps({'success' : success, 'message' : msg, 'total_checked_in' : newTotal}))


def getTotalFromDB():
    from models import Volunteer, Rep
    total_checked_in = Hacker.query(Hacker.checked_in == True).count()
    total_checked_in += Rep.query(Rep.checked_in == True).count()
    total_checked_in += Volunteer.query(Volunteer.checked_in == True).count()
    return total_checked_in

def getTotal(increment_first=False):
    key = 'total_checked_in'
    client = memcache.Client()
    retries = 5
    success = False
    total_checked_in = 0
    while retries > 0 and not success:
        total = client.gets(key)
        if total is None:
            total = getTotalFromDB()
            if increment_first:
                total += 1
            client.set(key, total)
            return total

        if increment_first:
            total += 1
        if client.cas(key, total):
            success = True
            return total

        retries -= 1

    return success

class MoreInfoHandler(webapp2.RequestHandler):
    def get(self, id):
        infoKeys = hacker_keys + ['checked_in', 'status']

        hacker = ndb.Key(urlsafe=id).get()
        hackerDict = hacker.asDict(infoKeys)
        hackerDict.update({'id' : id})

        optionalKeys = ['resume']
        missingOptional = [key for key in optionalKeys if not getattr(hacker, key, None)]

        required = {}
        if hacker.year == "highschool":
            required.update({'Parental Waiver' : 'Confirm this hacker is 18 or has a waiver.'})


        if hacker.phone_number is None:
            required.update({'Phone Number' : "Enter this hacker's phone number"})

        defaultReminders = ['Remind this hacker about food or something.', 'Remind this hacker that travel receipts are due on 1.2.2015']

        self.response.write(json.dumps({'hacker': hackerDict, 'missingOptionalInfo' : missingOptional, 'requiredInfo' : required, 'reminders' : defaultReminders}))

class AddRequiredInfoHandler(webapp2.RequestHandler):
    def post(self):
        request = json.loads(self.request.body)
        id = request.get('id')
        phone_number = request.get('phone_number')
        if not id or not phone_number:
            return self.response.write(json.dumps({'success' : False}))

        person = ndb.Key(urlsafe=id).get()
        if not person:
            logging.info('no person')
            return self.response.write(json.dumps({'success' : False}))
        try:
            if person.key.kind() == 'Hacker':
                person.phone_number = phone_number
            elif person.key.kind() == 'Volunteer':
                person.phone = phone_number
            else:
                return self.response.write(json.dumps({'success' : False}))
            person.put()
        except datastore_errors.BadValueError as err:
            return self.response.write(json.dumps({'success' : False}))

        self.response.write(json.dumps({'success' : True}))

class CreateNewPersonHandler(webapp2.RequestHandler):
    def post(self):
        request = json.loads(self.request.body)
        kind = request.get('kind')

        if kind == 'Hacker':
            hacker = {'email' : request.get('email'), 'name' : request.get('name'), 'checked_in' : True}
            return self.response.write(json.dumps({'success':registration.create_hacker(hacker)
            }))
        elif kind == 'Visitor':
            person = models.Visitor()
        elif kind == 'Volunteer':
            person = models.Volunteer()
        elif kind == 'Rep':
            person = models.Rep()
        else:
            return self.response.write(json.dumps({'sucess' : False}))

        try:
            for field in request.get('fields'):
                setattr(person, field, request.get(field))
            setattr(person, 'checked_in', True)
            person.put()
        except datastore_errors.BadValueError as err:
            return self.response.write(json.dumps({'success':False, 'msg' : err.args[0]}))

        self.response.write(json.dumps({'success' : True}))


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

class DisconnectSessionHandler(webapp2.RequestHandler):
    def post(self):
        client_id = self.request.get('from')
        if client_id is not None:
            session = ndb.Key(urlsafe=client_id).get()
            session.active=False
            session.put()

app = webapp2.WSGIApplication([
    ('/checkin', CheckinPageHandler),
    ('/checkin/new', CreateNewPersonHandler),
    ('/checkin/info/(.+)', MoreInfoHandler),
    ('/checkin/requiredInfo', AddRequiredInfoHandler),
    ('/_ah/channel/disconnected/', DisconnectSessionHandler)
], debug=True)
