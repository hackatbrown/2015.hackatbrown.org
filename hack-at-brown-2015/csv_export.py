import csv
import webapp2
from registration import Hacker, hacker_keys, non_required_keys, personal_info_keys
from config import onTeam, isAdmin
import logging

class CsvExport(webapp2.RequestHandler):
    def get(self):
        if not onTeam(): return self.redirect('/')

        keys = list(set(list(hacker_keys) + list(personal_info_keys) + list(non_required_keys) + ['status', 'admit_priority', 'rsvpd', 'checked_in', 'has_resume', 'secret', 'address1', 'address2', 'city', 'state', 'country', 'zip']))
        if (not self.request.get('include_personally_identifiable_info')) or not isAdmin():
            for key in personal_info_keys:
                keys.remove(key)
        self.response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        writer = csv.DictWriter(self.response, fieldnames=keys)
        writer.writeheader()
        for hacker in Hacker.query():
          writer.writerow({key: unicode(val).encode('utf-8') for key, val in hacker.asDict(keys).iteritems()})
