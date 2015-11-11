import os
from google.appengine.api.app_identity import get_application_id
from google.appengine.api import users

"""
This file contains various settings for the hackathon.
"""

SIGN_UP_FOR_UPDATES = "sign_up_for_updates"
REGISTRATION_OPEN = "registration_open"
REGISTRATION_CLOSED = "registration_closed"

def registration_status():
    return REGISTRATION_CLOSED

def should_rank_hackers():
    return False

def should_send_admissions():
	return False

def should_email_teammates():
    return False

def should_send_apologies():
    return False

def send_confirmation_apologies():
    return False

def admissions_limit():
	return 370

def admission_expiration_seconds():
	return 60 * 60 * 24 * 7

def checkin_limit():
  return 370

def envIsDev():
    DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')
    return DEV

def envIsQA():
    appname = get_application_id()
    return appname == "hackatbrown2015-dev"

def isMasterDB():
    return not (envIsDev() or envIsQA() or self.request.host.split(":")[0] != "localhost")

def isAdmin():
  return users.is_current_user_admin()

def onTeam():
  from team import members
  emails = members
  user = users.get_current_user()
  if user is None:
      return False

  return user.email() in emails or isAdmin()
