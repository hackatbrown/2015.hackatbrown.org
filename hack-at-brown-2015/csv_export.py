import csv
import webapp2
from registration import Hacker, hacker_keys, personal_info_keys
from hacker_page import computeStatus
from config import onTeam, isAdmin

def dict_from_hacker(hacker, include_keys):
    d = {key: getattr(hacker, key, None) for key in include_keys}
    d['status'] = computeStatus(hacker)
    d['has_resume'] = False if (not hasattr(hacker, 'resume') or hacker.resume == {} or hacker.resume ==  None) else true
    return d

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
            writer.writerow(dict_from_hacker(hacker, keys))
