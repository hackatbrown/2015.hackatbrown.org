import webapp2
from updateSchema import updateSchema
from google.appengine.ext import deferred
import logging

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("HIT HANDLER")
        deferred.defer(updateSchema)
        self.response.out.write('Schema migration successfully initiated.')

app = webapp2.WSGIApplication([('/update_schema', UpdateHandler)])
