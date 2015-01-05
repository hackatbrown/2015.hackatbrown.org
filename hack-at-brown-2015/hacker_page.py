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

reimbursement_keys = ["address1", "address2", "city", "state", "zip", "country", "email", 'rtotal']


class HackerPageHandler(webapp2.RequestHandler):
    def get(self, secret):

        hacker = getHacker(secret)

        if hacker is None:
            self.redirect('/')
#            this shouldn't silently fail.  we should make a 404
            return

        status = computeStatus(hacker)
        resumeFileName = ""
        receiptsFileNames = ""

        if hacker.resume:
            resumeFileName = hackerFiles.getFileName(hacker.resume)

        if hacker.receipts and hacker.receipts[0] != None:
            receiptsFileNames = hackerFiles.getFileNames(hacker.receipts)

        name = hacker.name.split(" ")[0] # TODO: make it better

        self.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        self.response.headers["Pragma"] = "no-cache"
        self.response.headers["Expires"] = "0"

        self.response.write(template.template("hacker_page.html", {"hacker": hacker, "status": status, "name": name, "resumeFileName" : resumeFileName, "receiptsFileNames" : receiptsFileNames}))

class DeleteHackerHandler(webapp2.RequestHandler):
    def get(self, secret):
        hacker = getHacker(secret)
        if hacker:
            createDeletedHacker(hacker, "unregistered")
            hacker.key.delete()
            memcachedKey = memcachedBase + secret
            memcache.set(memcachedKey, None, cacheTime)

        self.redirect('/goodbye')

class RSVPHandler(webapp2.RequestHandler):
    def post(self, secret):
        hacker = getHacker(secret)
        if hacker is None or hacker.admitted_email_sent_date is None:
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

        status = computeStatus(hacker)

        keys = registration.hacker_keys

        if (status == "checked in") or (status == "confirmed"):
            keys += reimbursement_keys

        kv = {}
        for key in parsed_request:
            if key in keys:
                value = parsed_request.get(key)
                if key == 'email':
                    continue
                if key == 'rtotal':
                    try:
                        value = int(value)
                        if value > hacker.rmax:
                            value = hacker.rmax
                    except Exception:
                        success = False
                        break
                    # logging.info("Update Hacker: " + hacker.name + " (" + secret + ") attr: " + key + " val: " + value)
                kv[key] = value

            else:
                logging.info("Key {0}not found or authorized".format(key))
                success = False

        if kv:
            success = updateHacker(secret, kv)

        if not success:
            self.response.set_status(400)

        self.response.write(json.dumps({"success": success}))

def updateHacker(secret, dict):
    memcachedKey = memcachedBase + secret
    client = memcache.Client()
    retries = 5
    success = False
    while retries > 0 and not success:
        hacker = client.gets(memcachedKey)
        if hacker is None:
            hacker = registration.Hacker.WithSecret(secret)
            client.set(memcachedKey, hacker)

        for k, v in dict.iteritems():
            setattr(hacker, k, v)


        if client.cas(memcachedKey, hacker):
            success = True
            hacker.put()

        retries-= 1

    return success

def getHacker(secret):
    memcachedKey = memcachedBase + secret
    client = memcache.Client()
    hacker = client.gets(memcachedKey)
    if hacker is None:
        hacker = registration.Hacker.WithSecret(secret)

    return hacker

def sendReimbursementFormToBrown(hacker):

    payload = {}

    payload["first_name"] = hacker.name.split(" ")[0]
    payload["last_name"] = hacker.name.split(" ")[1] if " " in hacker.name else "None"
    payload["phone"] = hacker.phone_number
    payload["department"] = "Computer Science: Hack At Brown"
    payload["Submit"] = "Submit"

    for key in reimbursement_keys:
        attr = getattr(hacker, key, "")
        if key != "address2" and attr == "":
            return False

        payload[key] = attr


    url = 'https://secure.brown.edu/purchasing/visitor/'

    failedHTML = '<div class="submitted"><span>Please make sure that all required fields are filled in.</span></div>'

    form_data = urllib.urlencode(payload)
    result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)
    return not (failedHTML in result.content)

def putHacker(hacker):

    if hacker.receipts == [None]:
        hacker.receipts = []
    memcachedKey = memcachedBase + hacker.secret
    client = memcache.Client()
    #TODO: consider using cas
    if not client.set(memcachedKey, hacker, cacheTime):
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
