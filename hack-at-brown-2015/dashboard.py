import webapp2
import datetime
import json
from registration import Hacker, accept_hacker
from send_email import send_email
from template import template
from email_list import EmailListEntry

class DashboardHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template("dashboard.html"))

class BreakdownHandlers(webapp2.RequestHandler):
    def get(self):
        self.response.write(template("dashboard.html"))

class ManualRegistrationHandler(webapp2.RequestHandler):
    def post(self):
        emails = self.request.get("emails")
        for address in emails:
            hacker = Hacker.query(Hacker.email == address).fetch()
            if hacker:
                for h in hacker: # should only be one
                    if h.admitted_email_sent_date != None:
                        accept_hacker(h)
                
              

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
    subject = self.request.get("subject")
    body = self.request.get("body")
    send_to = []
    if self.request.get("recipients") == "all":
        send_to = [hacker.email for hacker in Hacker.query()]
    elif self.request.get("recipients") == "waitlisted":
        send_to = [hacker.email for hacker in Hacker.query(Hacker.waitlist_email_sent_date != None)]
    elif self.request.get("recipients") == "accepted":
        send_to = [hacker.email for hacker in Hacker.query(Hacker.admitted_email_sent_date != None)]
    send_email(recipients=send_to, html=body, subject=subject)
    self.response.write(json.dumps({"success": True, "recipients": send_to }))
