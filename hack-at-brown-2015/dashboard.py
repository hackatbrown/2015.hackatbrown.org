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
from google.appengine.api import users
from config import onTeam, isAdmin
import deletedHacker

cacheTime = 6 * 10 * 2
memcachedBase = 'all_hackers_with_prop'

class DashboardHandler(webapp2.RequestHandler):
    def get(self):

        if not onTeam():
            logging.info("Not authorized")
            return self.redirect('/')

        isQA = envIsQA()
        isDev = envIsDev()

        self.response.write(template("dashboard.html", {"envIsDev" : isDev, "isQA" : isQA, "admin" : isAdmin(), "onTeam" : onTeam(), "logout" : users.create_logout_url('/')}))

class ManualRegistrationHandler(webapp2.RequestHandler):
    def post(self):
        if not isAdmin(): return self.redirect('/')
        parsed_request = json.loads(self.request.body) # Angular apparently only sends json as text not as 'JSON'
        emails = parsed_request.get('emails')
        for address in emails:
            hacker = Hacker.query(Hacker.email == address).fetch()
            if hacker:
                for h in hacker: # should only be one
                    if parsed_request.get('change') == "Accept":
                        if h.admitted_email_sent_date == None:
                            accept_hacker(h)

                    if parsed_request.get('change') == "Remove":
                        deletedHacker.createDeletedHacker(h, "manual")
                        h.key.delete()

                    if parsed_request.get('change') == 'Waitlist':
                        if h.admitted_email_sent_date == None:
                            waitlist_hacker(h)



class DashboardBackgroundHandler(webapp2.RequestHandler):
  def get(self):
    data = {}
    data['Signed Up'] = EmailListEntry.query().count()
    data['Registered'] = Hacker.query().count()
    data['Accepted'] = Hacker.query(Hacker.admitted_email_sent_date != None).count()
    data['Confirmed'] = Hacker.query(Hacker.rsvpd == True).count()
    data['Waitlisted'] = Hacker.query(Hacker.waitlist_email_sent_date != None).count()
    data['Declined'] = deletedHacker.DeletedHacker.query(deletedHacker.DeletedHacker.admitted_email_sent_date != None).count()

    self.response.write(json.dumps(data))

class RankingDashHandler(webapp2.RequestHandler):
  def get(self):
    if not isAdmin(): return self.redirect('/')
    self.response.write(template("ranking.html"))


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

class BreakdownHandler(webapp2.RequestHandler):
    def get(self, type):
        data = getBreakdown(type)
        self.response.write(json.dumps(data))

class FilteredBreakdownHandler(webapp2.RequestHandler):
    def get(self, type, filter):
        logging.info(type)
        logging.info(filter)
        accepted = (filter == "accepted")

        data = getBreakdown(type, accepted)
        self.response.write(json.dumps(data))

def getBreakdown(type, accepted=False):
    if type == 'all':
        data = getAll(accepted=accepted)
    elif type == 'diet':
        data = getByDietaryRestrictions(accepted=accepted)
    elif type == 'shirt':
        data = getByShirtSize(accepted=accepted)
    elif type == 'h_status':
        data = getByStatus(accepted=accepted)
    elif type == 'reimbursements':
        #We only care about reimbursements for accepted hackers
        data = getReimbursements()
    else:
        data = getGeneric(type, accepted=accepted)

    return data

def getAllHackers(projection=[], accepted=False):
    memcachedKey = memcachedBase + str(projection) + str(accepted)
    hackers = memcache.get(memcachedKey)
    if hackers is None:
        if projection:
            hackers = Hacker.query(projection=projection)
        else:
            hackers = Hacker.query()
        if accepted:
            hackers = hackers.filter(Hacker.admitted_email_sent_date != None)

        hackers = hackers.fetch()
        if not memcache.set(memcachedKey, hackers, cacheTime):
            logging.error("Memcache set failed")

    return hackers

def getReimbursements():
    allocated = {'name' : 'Allocated Budget'}
    spent =  {'name': 'Actual Spending'}
    allocatedData = {}
    spentData = {}
    hackers = getAllHackers(projection=['rmax', 'rtotal'], accepted=True)
    for hacker in hackers:
        rmax = hacker.rmax
        tier = "Tier " + str(rmax)
        allocatedData[tier] = allocatedData.setdefault(tier, 0) + rmax
        spentData[tier] = spentData.setdefault(tier, 0) + hacker.rtotal

    allocated['data'] = allocatedData
    spent['data'] = spentData
    return [allocated, spent]

def getAll(accepted=False):
    prettyKeys = {
    "School" : "school",
    "Shirt Size" : "shirt",
    "Hardware Hackers" : "hardware_hack",
    "First Timers" : "first_hackathon",
    "Dietary Restrictions" : "diet",
    "Year" : "year",
    "Gender" : "shirt_gen",
    "Admit Status" : "h_status",
    "State" : "state",
    }

    data = {}
    for pretty, key in prettyKeys.items():
        data[pretty] = getBreakdown(key, accepted)

    return data


def getGeneric(value, accepted=False):
    hackers = getAllHackers([value], accepted)
    data = {}
    for hacker in hackers:
        key = getattr(hacker, value)
        data[key] = data.setdefault(key, 0) + 1
    return data

def getByShirtSize(accepted=False):
    hackers =  getAllHackers(["shirt_gen", "shirt_size"], accepted)
    data = {}
    for hacker in hackers:
        key = hacker.shirt_gen + hacker.shirt_size
        data[key] = data.setdefault(key, 0) + 1
    return data

def getByDietaryRestrictions(accepted=False):
    hackers =  getAllHackers(["dietary_restrictions"], accepted)
    data = {}
    for hacker in hackers:
        multikey = hacker.dietary_restrictions
        if multikey == "":
            multikey = "None"

        for key in multikey.split(','):
            key = key.title()
            data[key] = data.setdefault(key, 0) + 1
    return data

def getByStatus(accepted=False):
    hackers = getAllHackers(accepted=accepted)
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

