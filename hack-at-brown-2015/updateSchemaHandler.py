import webapp2
from updateSchema import updateSchema
from google.appengine.ext import deferred
import logging
import config

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("HIT HANDLER")
        if config.isAdmin():
            deferred.defer(updateSchema)
            self.response.out.write('Schema migration successfully initiated.')
        else:
            self.response.out.write("Must be an admin")

app = webapp2.WSGIApplication([('/update_schema', UpdateHandler)])
