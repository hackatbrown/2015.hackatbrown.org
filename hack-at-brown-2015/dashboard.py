import webapp2
import datetime
import json
from registration import Hacker, accept_hacker
from send_email import send_email
from template import template
from email_list import EmailListEntry

import logging

class DashboardHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template("dashboard.html"))

class ManualRegistrationHandler(webapp2.RequestHandler):
    def post(self):
        parsed_request = json.loads(self.request.body)
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


class DashboardBackgroundHandler(webapp2.RequestHandler):
  def get(self):
    data = {}
    data['signup_count'] = EmailListEntry.query().count()
    data['registered_count'] = Hacker.query().count()
    data['accepted_count'] = Hacker.query(Hacker.admitted_email_sent_date != None).count()
    data['waitlist_count'] = Hacker.query(Hacker.waitlist_email_sent_date != None).count()
    data['declined_count'] = 0

    self.response.write(json.dumps(data))

class SendEmail(webapp2.RequestHandler):
  def post(self):
    parsed_request = json.loads(self.request.body)
    subject = parsed_request.get("subject")
    body = parsed_request.get("body")
    send_to = []
    if parsed_request.get("recipients") == "all":
        send_to = [hacker.email for hacker in Hacker.query()]
    elif parsed_request.get("recipients") == "waitlisted":
        send_to = [hacker.email for hacker in Hacker.query(Hacker.waitlist_email_sent_date != None)]
    elif parsed_request.get("recipients") == "accepted":
        send_to = [hacker.email for hacker in Hacker.query(Hacker.admitted_email_sent_date != None)]
    send_email(recipients=send_to, html=body, subject=subject)
    self.response.write(json.dumps({"success": True, "recipients": send_to }))

class ViewBreakdownsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template("breakdowns.html"))

class BreakdownHandler(webapp2.RequestHandler):
    def get(self, type):
        if type == 'school':
            data = getBySchool()
        elif type == 'all':
            data = getAll()
        elif type == 'shirt':
            data = getByShirtSize()
        elif type == 'diet':
            data = getByDietaryPreferences()
        else:
            data = {}

        self.response.write(json.dumps(data))

def getAll():
    hackers =  Hacker.query().fetch()
    schools = {}
    shirts = {}
    hardware = {}
    firstHack = {}
    diet = {}
    year = {}

    for hacker in hackers:
        schools[hacker.school] = schools.setdefault(hacker.school, 0) + 1
        year[hacker.year] = year.setdefault(hacker.year, 0) + 1
        shirts[hacker.shirt_gen] = shirts.setdefault(hacker.shirt_gen, 0) + 1
        shirts[hacker.shirt_gen + hacker.shirt_size] =  shirts.setdefault(hacker.shirt_gen + hacker.shirt_size, 0) + 1
        hardware[hacker.hardware_hack] = hardware.setdefault(hacker.hardware_hack, 0) + 1
        firstHack[hacker.first_hackathon] = firstHack.setdefault(hacker.first_hackathon, 0) + 1
        if hacker.dietary_restrictions == "":
            diet["No Info"] = diet.setdefault("No Info", 0) + 1
        else:
            diet[hacker.dietary_restrictions] = diet.setdefault(hacker.dietary_restrictions, 0) + 1
    return {"schools": schools, "shirts":shirts, "hardware": hardware, "firstHack": firstHack, "diet":diet, "year": year}

def getBySchool():
    hackers =  Hacker.query().fetch()
    data = {}
    for hacker in hackers:
        data[hacker.school] = data.setdefault(hacker.school, 0) + 1
    return data
def getByShirtSize():
    return None
def getByDietaryPreferences():
    return None



    #######
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
