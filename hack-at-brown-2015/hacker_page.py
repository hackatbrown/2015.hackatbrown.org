import webapp2
import template
import registration
import logging
import json
from google.appengine.api import memcache

cacheTime = 6 * 10
memcachedBase = 'hacker_update/'


class HackerPageHandler(webapp2.RequestHandler):
    def get(self, secret):
        memcachedKey = memcachedBase + secret
        hacker = memcache.get(memcachedKey)
        if hacker is None:
            hacker = registration.Hacker.WithSecret(secret)

        if hacker is None:
            self.redirect('/')

        status = computeStatus(hacker)
        name = hacker.name.split(" ")[0] # TODO: make it better
        self.response.write(template.template("hacker_page.html", {"hacker": hacker, "status": status, "name": name, "secret": secret}))

class HackerUpdateHandler(webapp2.RequestHandler):
    def post(self, secret):
        memcachedKey = memcachedBase + secret
        parsed_request = json.loads(self.request.body)

        hacker = memcache.get(memcachedKey)
        if hacker is None:
            hacker = registration.Hacker.WithSecret(secret)

        logging.info("Request for hacker update recieved: " + hacker.name)
        for key in parsed_request:
            logging.info("key: " + key)
            if key in registration.hacker_keys:
                logging.info("Update Hacker: " + hacker.name + " (" + secret + ") attr: " + key + " val: " + parsed_request.get(key))
                setattr(hacker, key, parsed_request.get(key))
            else:
                logging.info("Key not found")

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
