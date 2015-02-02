from google.appengine.ext import ndb
from google.appengine.api import datastore_errors

def stringValidator(prop, value):
   cleanValue = value.strip()

   if prop._name == 'email':
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
    checked_in = ndb.BooleanProperty(default=False)
    company = ndb.StringProperty(default=None, validator=stringValidator)

    def asDict(self, include_keys):
        return {key: getattr(self, key, None) for key in include_keys}

class Volunteer(ndb.Model):
    name = ndb.StringProperty(default=None, validator=stringValidator)
    email = ndb.StringProperty(default=None, validator=stringValidator)
    checked_in = ndb.BooleanProperty(default=False)
    phone = ndb.StringProperty(default=None, validator=phoneValidator)
    role = ndb.StringProperty(default=None, validator=stringValidator)

    def asDict(self, include_keys):
        return {key: getattr(self, key, None) for key in include_keys}

class CheckInSession(ndb.Model):
    user = ndb.StringProperty(default=None)
    active = ndb.BooleanProperty(default=True)
