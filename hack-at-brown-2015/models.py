from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
import logging

def stringValidator(prop, value):
   cleanValue = value.strip()

   if prop._name == 'email' or prop._name == 'requester_email':
           cleanValue = cleanValue.lower()

   return cleanValue

def phoneValidator(prop, value):
   if any(c.isalpha() for c in value):
       raise datastore_errors.BadValueError(prop._name)
   elif len(value) == 10:
       return value
   elif len(value) == 11 and value[0] == '1':
       return value[1:] # remove +1 US country code
   else:
       logging.info(value)
       raise datastore_errors.BadValueError(prop._name)

class Visitor(ndb.Model):
    name = ndb.StringProperty(default=None, validator=stringValidator)
    email = ndb.StringProperty(default=None, validator=stringValidator)
    checked_in = ndb.BooleanProperty(default=False)
    org = ndb.StringProperty(default=None, validator=stringValidator)

    def asDict(self, include_keys):
        return {key: getattr(self, key, None) for key in include_keys}

class Rep(ndb.Model):
    name = ndb.StringProperty(default=None, validator=stringValidator)
    email = ndb.StringProperty(default=None, validator=stringValidator)
    phone_number = ndb.StringProperty(default=None, validator=phoneValidator)
    checked_in = ndb.BooleanProperty(default=False)
    company = ndb.StringProperty(default=None, validator=stringValidator)
    shirt_gen = ndb.StringProperty(choices=['M', 'W'])
    shirt_size = ndb.StringProperty(choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])

    def asDict(self, include_keys):
        me = {key: getattr(self, key, None) for key in include_keys}
        if 'status' in include_keys:
          me['status'] = 'confirmed'
        return me

class Volunteer(ndb.Model):
    name = ndb.StringProperty(default=None, validator=stringValidator)
    email = ndb.StringProperty(default=None, validator=stringValidator)
    checked_in = ndb.BooleanProperty(default=False)
    phone_number = ndb.StringProperty(default=None, validator=phoneValidator)
    role = ndb.StringProperty(default=None, validator=stringValidator)
    shirt_gen = ndb.StringProperty(choices=['M', 'W'])
    shirt_size = ndb.StringProperty(choices=['XS', 'S', 'M', 'L', 'XL', 'XXL'])

    def asDict(self, include_keys):
        me = {key: getattr(self, key, None) for key in include_keys}
        if 'status' in include_keys:
          me['status'] = 'confirmed'
        return me


class CheckInSession(ndb.Model):
    user = ndb.StringProperty(default=None)
    active = ndb.BooleanProperty(default=True)
