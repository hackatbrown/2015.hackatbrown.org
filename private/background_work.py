import webapp2
from registration import Hacker, accept_hacker, expire_hacker
import config
import datetime
from send_email import send_email
from template import template
from google.appengine.api import memcache

"""
gotta put id's of just-accepted people in memcached b/c just-updated records
might not appear in query results immediately thanks to eventual consistency!
"""
memcache_expiry = 10 * 60

# TODO: secure this from being run by a third-party using the instructions at https://cloud.google.com/appengine/docs/python/config/cron

class BackgroundWorkHandler(webapp2.RequestHandler):
	def get(self):
		if config.should_send_admissions():
			accept_hackers()


def printStats():
	print "=====RUNNING THE NUMBERS====="
	hackers_accepted = Hacker.query(Hacker.admitted_email_sent_date != None).fetch()
	total_accepted = 0
	hackers_to_expire = 0
	rsvpd_hackers = 0
	for hacker in hackers_accepted:
		total_accepted += 1
		if hacker.rsvpd == True:
			rsvpd_hackers += 1
		elif (hacker.deadline - datetime.datetime.now()).days < 0:
			hackers_to_expire +=1

	print "Total Accepted: " + str(total_accepted)
	print "RSVP'd Hackers: " + str(rsvpd_hackers)
	print "Hackers to expire: " + str(hackers_to_expire)
	print "=====END STATS====="


def accept_hackers():
	expire_acceptances()
	admitted_count = Hacker.query(Hacker.admitted_email_sent_date != None).count()
	print "admitted count: " + str(admitted_count)
	more_to_admit = config.admissions_limit() - admitted_count
	print "more to admit: " + str(more_to_admit)
	if more_to_admit > 0:
		for hacker in Hacker.query(Hacker.admitted_email_sent_date == None).order(-Hacker.admit_priority).fetch(more_to_admit):
			if hasattr(hacker, 'admitted_email_sent_date') and hacker.admitted_email_sent_date != None:
				print "tried accepting already accepted hacker for some reason"
				continue 
			print "Admiting " + hacker.name + ": " + hacker.email + " with rank " +  str(hacker.admit_priority)
			accept_hacker(hacker)

def waitlist_hackers():
	for hacker in Hacker.query(Hacker.admitted_email_sent_date == None, Hacker.waitlist_email_sent_date == None):
		waitlist_hacker(hacker)


def waitlist_hacker(hacker):
	if memcache.get("admitted:{0}".format(hacker.secret)) != None:
		return False # we _just_ accepted this user, but it hasn't been reflected by the query yet

	email = template("emails/waitlisted.html", {"hacker": hacker, "name":hacker.name.split(" ")[0]})
	send_email(recipients=[hacker.email], html=email, subject="You're on the waitlist for Hack@Brown")

	hacker.waitlist_email_sent_date = datetime.datetime.now()
	hacker.put()
	return True


def expire_acceptances():
	for hacker in Hacker.query(Hacker.admitted_email_sent_date != None):
		if (hacker.deadline - datetime.datetime.now()).days < 0:
			if hacker.rsvpd != True:
				print "hacker with negative deadline: "+ hacker.email
				expire_hacker(hacker)
		elif (hacker.deadline - datetime.datetime.now()).days == 0 and hacker.rsvp_reminder_sent_date == None:
			if hacker.rsvpd != True:
				print "sending rsvp reminder"
				email = template("emails/rsvp_reminder.html", {"hacker": hacker, "name":hacker.name.split(" ")[0], "rmax": hacker.rmax})
				send_email(recipients=[hacker.email], html=email, subject="It's your last day to RSVP for Hack@Brown!")

				hacker.rsvp_reminder_sent_date = datetime.datetime.now()
				hacker.put()
			elif hacker.rtotal == 0 and hacker.rmax > 0:
				print "sending reimbursement reminder"
				email = template("emails/reimbursement_reminder.html", {"hacker": hacker, "name":hacker.name.split(" ")[0],"rmax": hacker.rmax})
				send_email(recipients=[hacker.email], html=email, subject="Last day to request a reimbursement from Hack@Brown")
				hacker.rsvp_reminder_sent_date = datetime.datetime.now()
				hacker.put()



def email_teammates():
	for hacker in Hacker.query(Hacker.teammates_emailed == None or Hacker.teammates_emailed == False ).fetch():
		email_html = template("emails/teammate.html", {"name": hacker.name.split(" ")[0]})
		sub = hacker.name.split(" ")[0] + " invited you to Hack@Brown!"
		send_to = []
		for email in hacker.teammates.split(","):
			if Hacker.query(Hacker.email == email).count() == 0:
				send_to.append(email)
		send_email(recipients=send_to, subject=sub, html=email_html)
		hacker.teammates_emailed = True
		hacker.put()


def resend_registration_emails():
	count = 0
	for hacker in Hacker.query().fetch():
		if hasattr(hacker, 'post_registration_email_sent_date'):
			if hacker.post_registration_email_sent_date == None:
				#hacker has the field, but email wasn't sent.
				#send_missed_email(hacker)
				count += 1
		else:
			#hacker doesn't have the field at all, so send and set.
			#send_missed_email(hacker)
			count += 1
	print "Resending emails to " + str(count) + " hackers"


def send_missed_email(hacker):
	email_html = template("emails/registration_apology.html", {"name": hacker.name.split(" ")[0], "hacker": hacker})
	send_email(recipients=[hacker.email], subject="You've applied to Hack@Brown!", html=email_html)
	hacker.post_registration_email_sent_date = datetime.datetime.now()
	hacker.put()

def send_confirmation_apologies():
	f = open("emails_we_sent_to")
	emails_we_sent_to = []
	for email in f.readlines():
		emails_we_sent_to.append(email.strip())
	for hacker in Hacker.query().fetch():
		#skip everyone we already sent to.
		if hacker.email in emails_we_sent_to:
			continue
		email_html = template("emails/confirmation_apology.html", {"name": hacker.name.split(" ")[0], "hacker": hacker})
		send_email(recipients=[hacker.email], subject="Registration Clarifications", html=email_html)

