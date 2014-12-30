import webapp2
import datetime
import json
from registration import Hacker, accept_hacker
from send_email import send_email
from template import template
from email_list import EmailListEntry
from hacker_page import computeStatus
from background_work import waitlist_hacker
from google.appengine.api import memcache
import logging
from config import envIsDev, envIsQA
import itertools
from google.appengine.ext import ndb

cacheTime = 6 * 10 * 2
memcachedBase = 'all_hackers_with_prop'

class DashboardHandler(webapp2.RequestHandler):
    def get(self):
        isQA = envIsQA()
        isDev = envIsDev()
        self.response.write(template("dashboard.html", {"envIsDev" : isDev, "isQA" : isQA}))

class ManualRegistrationHandler(webapp2.RequestHandler):
    def post(self):
        parsed_request = json.loads(self.request.body) # Angular apparently only sends json as text not as 'JSON'
        emails = parsed_request.get('emails')
        for address in emails:
            hacker = Hacker.query(Hacker.email == address).fetch()
            if hacker:
                for h in hacker: # should only be one
                    if parsed_request.get('change') == "Register":
                        if h.admitted_email_sent_date == None:
                            accept_hacker(h)

                    if parsed_request.get('change') == "Remove":
                        if h.admitted_email_sent_date == None:
                            h.key.delete()

                    if parsed_request.get('change') == 'Waitlist':
                        if h.admitted_email_sent_date == None:
                            waitlist_hacker(h)



class DashboardBackgroundHandler(webapp2.RequestHandler):
  def get(self):
    data = {}
    data['signup_count'] = EmailListEntry.query().count()
    data['registered_count'] = Hacker.query().count()
    data['accepted_count'] = Hacker.query(Hacker.admitted_email_sent_date != None).count()
    data['waitlist_count'] = Hacker.query(Hacker.waitlist_email_sent_date != None).count()
    data['declined_count'] = 0

    self.response.write(json.dumps(data))

class LookupHackerHandler(webapp2.RequestHandler):
    def get(self, emails):
        response = {'found' : [], 'notFound' : []}

        if (emails == 'feeling_lucky'):
            #I'm feeling lucky!
            luckyHacker = Hacker.query().get()
            response['found'].append({'email': luckyHacker.email, 'secret' : luckyHacker.secret})
            return self.response.write(json.dumps(response))

        emails = emails.split(',')



        for email in emails:
            hacker = Hacker.query(Hacker.email == email).fetch(projection=Hacker.secret)
            if len(hacker) > 0:
                response['found'].append({'email' : email, 'secret' : hacker[0].secret})
            else:
                response['notFound'].append(email)

        self.response.write(json.dumps(response))

class ViewBreakdownsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template("breakdowns.html"))

class BreakdownHandler(webapp2.RequestHandler):
    def get(self, type):
        data = getBreakdown(type)
        self.response.write(json.dumps(data))

def getBreakdown(type):
    if type == 'all':
        data = getAll()
    elif type == 'diet':
        data = getByDietaryRestrictions()
    elif type == 'shirt':
        data = getByShirtSize()
    elif type == 'h_status':
        data = getByStatus()
    else:
        data = getGeneric(type)

    return data

def getAllHackers(projection=None):

    if projection:
        memcachedKey = memcachedBase + str(projection)
        hackers = memcache.get(memcachedKey)
        if hackers is None:
            hackers = Hacker.query(projection=projection).fetch()
            if not memcache.set(memcachedKey, hackers, cacheTime):
                logging.error("Memcache set failed")
    else:
        hackers = Hacker.query(projection=projection).fetch()

    return hackers

def getAll():
    keys = ["school", "shirt", "hardware_hack", "first_hackathon", "diet",
    "year", "shirt_gen", "h_status"]
    data = {}
    for key in keys:
        data[key] = getBreakdown(key)

    return data


def getGeneric(value):
    hackers = getAllHackers([value])
    data = {}
    for hacker in hackers:
        key = getattr(hacker, value)
        data[key] = data.setdefault(key, 0) + 1
    return data

def getByShirtSize():
    hackers =  getAllHackers(["shirt_gen", "shirt_size"])
    data = {}
    for hacker in hackers:
        key = hacker.shirt_gen + hacker.shirt_size
        data[key] = data.setdefault(key, 0) + 1
    return data

def getByDietaryRestrictions():
    hackers =  getAllHackers(["dietary_restrictions"])
    data = {}
    for hacker in hackers:
        multikey = hacker.dietary_restrictions
        if multikey == "":
            multikey = "None"

        for key in multikey.split(','):
            key = key.title()
            data[key] = data.setdefault(key, 0) + 1
    return data

def getByStatus():
    hackers = getAllHackers()
    data = {}
    for hacker in hackers:
        key = computeStatus(hacker)
        data[key] = data.setdefault(key, 0) + 1
    return data

'''
    def entries_that_fit(offset):
    entries = 0
    size = 0
    for reg in Registration.query(Registration.accepted_date != None).order(Registration.accepted_date).iter(offset=offset):
        if reg.resume_key:
            blobinfo = BlobInfo.get(reg.resume_key)
            if entries > 0 and size + blobinfo.size > MAX_SIZE:
                break
            else:
                size += blobinfo.size
        entries += 1
    return entries

import string
def strip_name(n):
    allowed_chars = string.ascii_letters + ' '
    return ''.join([c for c in n if c in allowed_chars])

import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
def zip_resumes(zipfile, offset, count):
    i = offset
    for reg in Registration.query(Registration.accepted_date != None).order(Registration.accepted_date).iter(offset=offset, limit=count):
        name = strip_name(reg.name) if reg.name else 'null'
        if reg.resume_key:
            blobinfo = BlobInfo.get(reg.resume_key)
            reader = blobinfo.open()
            filename = strip_name(reg.name)+' '+str(i)+' '+blobinfo.filename
            zipfile.writestr(filename, reader.read())
            reader.close()
        i += 1

class ResumeHandler(webapp2.RequestHandler):
    def get(self):
        offset = int(self.request.get('offset'), 0)
        resume_count = entries_that_fit(offset)
        self.response.write(template('resumes.html', {"offset": offset, "count": resume_count}))
    def post(self):
        offset, count = int(self.request.get('offset')), int(self.request.get('count'))
        self.response.headers['Content-Type'] ='application/zip'
        self.response.headers['Content-Disposition'] = 'attachment; filename="resumes %i-%i.zip"'%(offset,count)
        data = StringIO.StringIO()
        zipfile = ZipFile(data, "w", ZIP_DEFLATED)
        zip_resumes(zipfile, offset, count)
        zipfile.close()
        self.response.write(data.getvalue())

import collections
class BreakdownHandler(webapp2.RequestHandler):
    def get(self):
        bd_fields = ['school', 'shirt_size', 'dietary_restrictions']
        bd_counts = {field: collections.defaultdict(int) for field in bd_fields}
        for reg in Registration.query(Registration.accepted_date != None).iter():
            for field in bd_fields:
                val = getattr(reg, field)
                bd_counts[field][val] += 1
        bd_counts_as_tuples = {field: sorted(count_dict.items(), key=lambda (k,v): v, reverse=True) for field, count_dict in bd_counts.iteritems()}
        self.response.write(template('breakdowns.html', {"field_counts": bd_counts_as_tuples}))
'''


class NormalizeEmailsHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("<form method='POST'><input type='submit' value='Do it'/></form>")
	def post(self):
		to_put = []
		for h in itertools.chain(Hacker.query(), EmailListEntry.query()):
			if h.email != h.email.lower():
				h.email = h.email.lower()
				to_put.append(h)
		ndb.put_multi(to_put)
		self.response.write("Well, it seemed to work...")

