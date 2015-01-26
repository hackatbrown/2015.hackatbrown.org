import csv
import webapp2
from registration import Hacker, hacker_keys, personal_info_keys
from config import onTeam, isAdmin
import logging

class CsvExport(webapp2.RequestHandler):
    def get(self):
        if not onTeam(): return self.redirect('/')

        keys = list(hacker_keys) + ['status', 'admit_priority', 'rsvpd', 'checked_in', 'has_resume']
        if (not self.request.get('include_personally_identifiable_info')) or not isAdmin():
            for key in personal_info_keys:
                keys.remove(key)
        self.response.headers['Content-Type'] = 'text/csv'
        writer = csv.DictWriter(self.response, fieldnames=keys)
        writer.writeheader()
        for hacker in Hacker.query():
            try:
                writer.writerow(dict_from_hacker(hacker, keys))
            except UnicodeEncodeError:
                logging.error('could not encode\n')
                print(hacker)
            writer.writerow(hacker.asDict(keys))
