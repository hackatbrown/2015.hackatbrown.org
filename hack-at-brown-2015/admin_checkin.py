import logging
import webapp2
import json
from template import template
from registration import Hacker
from google.appengine.api import memcache

cacheTime = 6 * 10
hackerFormat = ['name', 'email']
divider = ' - '


class CheckinPageHandler(webapp2.RequestHandler):

    def get(self):

        #Can't use statements in lambdas :(
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

        response = template(
            "checkin_page.html", {"source": json.dumps(source)})

        self.response.write(response)

    def post(self):
        nameNemail = self.request.get('name/email').split(divider)
        hacker = Hacker.query(Hacker.name == nameNemail[0]
                              and Hacker.email == nameNemail[1]).fetch(1)[0]
        hacker.checked_in = True
        hacker.put()
        self.redirect('/admin_checkin')


def getHackersToBeChecked():
    # Cache this value, results don't need to be updated quickly.
    toCheckIn = 'hackers_to_be_checked'
    data = memcache.get(toCheckIn)
    if data is not None:
        logging.debug("Used cache")
        return data
    else:
        data = Hacker.query(Hacker.rsvpd == True
                            and Hacker.checked_in != True).fetch(
            projection=[Hacker.name, Hacker.email])
        logging.debug("Could not use cache")
        if not memcache.add(toCheckIn, data, cacheTime):
            logging.error('Memcache set failed')
    return data

app = webapp2.WSGIApplication([
    ('/admin_checkin', CheckinPageHandler),
], debug=True)
