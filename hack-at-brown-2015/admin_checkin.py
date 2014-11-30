import logging
import webapp2
import json
from template import template
from registration import Hacker
from google.appengine.api import memcache

cache_time = 6 * 10
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

        source = map(formatter, get_hackers_to_be_checked())

        response = template(
            "checkin_page.html", {"source": json.dumps(source)})

        self.response.write(response)

    def post(self):
        name_email = self.request.get('name/email').split(divider)
        hacker = Hacker.query(Hacker.name == name_email[0]
                              and Hacker.email == name_email[1]).fetch(1)[0]
        hacker.checked_in = True
        hacker.put()
        self.redirect('/admin_checkin')


def get_hackers_to_be_checked():
    # Cache this value, results don't need to be updated quickly.
    to_check_in = 'hackers_to_be_checked'
    data = memcache.get(to_check_in)
    if data is not None:
        logging.info("Used cache")
        return data
    else:
        data = Hacker.query(Hacker.rsvpd == True
                            and Hacker.checked_in != True).fetch(
            projection=[Hacker.name, Hacker.email])
        logging.info("Could not use cache")
        if not memcache.add(to_check_in, data, cache_time):
            logging.error('Memcache set failed')
    return data


def check_in_hacker(hacker):
    hacker.check_in = True
    # Do we also use memcache here?
    hacker.put()


app = webapp2.WSGIApplication([
    ('/admin_checkin', CheckinPageHandler),
], debug=True)
