import webapp2
import template
import registration
import logging
import json
from google.appengine.api import memcache
import hackerFiles
from deletedHacker import createDeletedHacker
from google.appengine.api import urlfetch
import urllib

cacheTime = 6 * 10
memcachedBase = 'hacker_update/'

class HackerPageHandler(webapp2.RequestHandler):
    def get(self, secret):

        hacker = getHacker(secret)

        if hacker is None:
            self.redirect('/')
            return

        status = computeStatus(hacker)
        resumeFileName = ""
        receiptsFileName = ""

        if hacker.resume:
            resumeFileName = hackerFiles.getFileName(hacker.resume)

        if hacker.receipts:
            receiptsFileName = hackerFiles.getFileName(hacker.receipts)



        name = hacker.name.split(" ")[0] # TODO: make it better

        self.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Pragma"] = "no-cache"
        self.response.headers["Expires"] = "0"

        self.response.write(template.template("hacker_page.html", {"hacker": hacker, "status": status, "name": name, "resumeFileName" : resumeFileName, "receiptsFileName" : receiptsFileName}))

class DeleteHackerHandler(webapp2.RequestHandler):
    def get(self, secret):
        hacker = getHacker(secret)
        if hacker:
            createDeletedHacker(hacker, "unregistered")
            hacker.key.delete()
            memcachedKey = memcachedBase + secret
            memcache.set(memcachedKey, None, cacheTime)

        self.redirect('/')

class RSVPHandler(webapp2.RequestHandler):
    def post(self, secret):
        hacker = getHacker(secret)
        if hacker is None:
            return self.response.write(json.dumps({"success":False}))

        hacker.rsvpd = True
        putHacker(hacker)
        return self.response.write(json.dumps({"success": True}))

class HackerUpdateHandler(webapp2.RequestHandler):
    def post(self, secret):
        parsed_request = json.loads(self.request.body)

        hacker = getHacker(secret)
        if hacker is None:
            return self.response.write(json.dumps({"success": False}))

        for key in parsed_request:
            logging.info("key: " + key)
            if key in registration.hacker_keys:
                requestKey = parsed_request.get(key)
                if requestKey != 'email':
                    logging.info("Update Hacker: " + hacker.name + " (" + secret + ") attr: " + key + " val: " + requestKey)
                    setattr(hacker, key, requestKey)
            else:
                logging.info("Key not found")

        putHacker(hacker)

        self.response.write(json.dumps({"success": True}))

def getHacker(secret):
    logging.info(secret)
    memcachedKey = memcachedBase + secret
    hacker = memcache.get(memcachedKey)
    if hacker is None:
        hacker = registration.Hacker.WithSecret(secret)

    return hacker

def sendFormToBrown(payload):
    url = 'https://secure.brown.edu/purchasing/visitor/'

    failedHTML = '<div class="submitted"><span>Please make sure that all required fields are filled in.</span></div>'


    payload["department"] = "Computer Science: Hack At Brown"
    payload["Submit"] = "Submit"

    form_data = urllib.urlencode(payload)
    result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)
    return not (failedHTML in result.content)

class SendToBrownHandler(webapp2.RequestHandler):
    def post(self, secret):
        keys = ["address1", "address2", "city", "state", "zip", "country"]

        hacker = getHacker(secret)
        payload = {}

        payload["email"] = hacker.email
        payload["first_name"] = hacker.name.split(" ")[0]
        payload["last_name"] = hacker.name.split(" ")[1]
        payload["phone"] = hacker.phone_number

        for key in keys:
            payload[key] = self.request.get(key)

        success = sendFormToBrown(payload)
        return self.response.write(json.dumps({"success": success}))



def putHacker(hacker):
    memcachedKey = memcachedBase + hacker.secret

    if not memcache.set(memcachedKey, hacker, cacheTime):
        logging.error('Memcache set failed')

    hacker.put()

def computeStatus(hacker):
    if hacker is None:
        return "not found"
    if hacker.checked_in == True:
        return "checked in"
    elif hacker.rsvpd == True:
        return "confirmed"
    elif hacker.admitted_email_sent_date != None:
        return "accepted"
    elif hacker.waitlist_email_sent_date != None:
        return "waitlisted"
    else:
        return "pending"
