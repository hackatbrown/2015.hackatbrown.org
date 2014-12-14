import webapp2
import template
import registration
import logging
import json
from google.appengine.api import memcache

cacheTime = 6 * 10

class HackerPageHandler(webapp2.RequestHandler):
    def get(self, secret):
        hacker = registration.Hacker.WithSecret(secret)

        if hacker is None:
            self.redirect('/')

        status = computeStatus(hacker)
        name = hacker.name.split(" ")[0] # TODO: make it better
        self.response.write(template.template("hacker_page.html", {"hacker": hacker, "status": status, "name": name}))

class HackerUpdateHandler(webapp2.RequestHandler):
    def post(self, secret):
        memcachedKey = 'hacker_update/' + secret
        parsed_request = json.loads(self.request.body)

        hacker = memcache.get(memcachedKey)
        if hacker is None:
            hacker = registration.Hacker.WithSecret(secret)

        for key in parsed_request:
            if key in registration.hacker_keys:
                setattr(hacker, key, parsed_request.get(key))

        if not memcache.set(memcachedKey, hacker, cacheTime):
            logging.error('Memcache set failed')

        hacker.put()

        self.response.write(json.dumps({"success": True}))

def computeStatus(hacker):
    if hacker is None:
        return "Not Found"

    if hacker.checked_in == True:
        return "Checked In"
    elif hacker.rsvpd == True:
        return "RSVP'd"
    elif hacker.admitted_email_sent_date != None:
        return "Registered"
    elif hacker.waitlist_email_sent_date != None:
        return "Waitlisted"
    else:
        return "Pending"
