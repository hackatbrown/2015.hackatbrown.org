import logging
import webapp2
import json
from template import template
from registration import Hacker
from google.appengine.ext import ndb
from google.appengine.api import memcache

cache_time = 6 * 10

class CheckinPageHandler(webapp2.RequestHandler):
    def get(self):
        hacker_names = map(lambda hacker: hacker.name, get_hackers_to_be_checked())

        response = template("checkin_page.html", {"hacker_names": json.dumps(hacker_names)})

        self.response.write(response)
        self.response.headers["Content-Type"] = "text/HTML"

def get_hackers_to_be_checked():
    # Cache this value, results don't need to be updated quickly.
    to_check_in = 'hackers_to_be_checked'
    data = memcache.get(to_check_in)
    if data is not None:
        logging.info("Used cache")
        return data
    else:
        data = Hacker.query(Hacker.rsvpd == True and Hacker.checked_in != True).fetch(projection=[Hacker.name])
        logging.info("Could not use cache")
        if not memcache.add(to_check_in, data, cache_time):
            logging.error('Memcache set failed')
    return data

def check_in_hacker(hacker):
    hacker.check_in = True
    #Do we also use memcache here?
    hacker.put()


app = webapp2.WSGIApplication([
    ('/admin_checkin', CheckinPageHandler)
], debug=True)


