import logging
import webapp2
import json
from template import template
from registration import Hacker
from google.appengine.api import memcache
from google.appengine.ext import ndb

cacheTime = 6 * 10
hackerFormat = ['name', 'email']
divider = ' - '


class CheckinPageHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write(page_response())

    def post(self):
        nameAndEmail = self.request.get('name/email').split(divider)
        hacker = Hacker.query(Hacker.name == nameAndEmail[0] and Hacker.email == nameAndEmail[1]).get()
        if hacker is None:
            success = False
        else:
            success = True
            hacker.checked_in = True
            hacker.put()

        successMsg = "successfully checked in " + hacker.name
        failureMsg = "failed to check in " + nameAndEmail[0]

        success = True

        self.response.write(page_response(success, successMsg if success else failureMsg))

        self.redirect('/admin_checkin')

def page_response(success=None, message=""):
    def formatter(hacker):
        formattedString = ''
        first = True
        for key in hackerFormat:
            if not first:
                formattedString += divider

            formattedString += getattr(hacker, key)
            first = False
        return formattedString

    source = map(formatter, getHackersToBeChecked())

    return template("checkin_page.html", {"source" : json.dumps(source),
                    "status" : json.dumps(success), "message" : message})

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

app = webapp2.WSGIApplication([
    ('/admin_checkin', CheckinPageHandler),
], debug=True)
