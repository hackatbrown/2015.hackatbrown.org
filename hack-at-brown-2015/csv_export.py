import csv
import webapp2
from registration import Hacker, hacker_keys, personal_info_keys
from hacker_page import computeStatus

def dict_from_hacker(hacker, include_keys):
    d = {key: getattr(hacker, key, None) for key in include_keys}
    d['status'] = computeStatus(hacker)
    return d

class CsvExport(webapp2.RequestHandler):
    def get(self):
        keys = list(hacker_keys) + ['status']
        if not self.request.get('include_personally_identifiable_info'):
            for key in personal_info_keys:
                keys.remove(key)
        self.response.headers['Content-Type'] = 'text/csv'
        writer = csv.DictWriter(self.response, fieldnames=keys)
        writer.writeheader()
        for hacker in Hacker.query():
            writer.writerow(dict_from_hacker(hacker, keys))
