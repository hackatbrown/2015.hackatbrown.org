import webapp2
from google.appengine.ext import ndb
from dashboard import getAllHackers
from registration import Hacker
import json
from template import template
from registration import hacker_keys
from config import envIsDev

#Example:
# json = {
#     "Rhode Island School of Design" : "Rhode Island School of Design"
#     "RISD" : "Rhode Island School of Design"
# }
# run('school', json)
class CleanupHandler(webapp2.RequestHandler):
    def post(self):
        parsed_request = json.loads(self.request.body)
        property = parsed_request.get('property')
        jsonKeys = parsed_request.get('jsonKeys')
        result =  run(property, jsonKeys)
        return self.response.write(json.dumps(result))

    def get(self):
        jinjaVars = {"properties" : hacker_keys}
        return self.response.write(template("db_cleanup.html", jinjaVars))

def run(property, jsonKeys):
    hackers = Hacker.query().filter(Hacker._properties[property].IN(jsonKeys.keys()))
    changed = []
    for hacker in hackers:
        newProp = jsonKeys.get(getattr(hacker, property, None), None)
        print(newProp)
        if newProp:
            setattr(hacker, property, newProp)
            changed.append(hacker)

    try:
        ndb.put_multi(changed)
    except Exception as err:
        return {"success":False, "msg": str(err.args[0])}

    successMsg = "Changed the " + property + " of " + str(len(changed)) + " hackers."
    return {"success":True, "msg": successMsg}

class PopulateHandler(webapp2.RequestHandler):
    def get(self, number):
        if not envIsDev() or self.request.host.split(":")[0] != "localhost":
            return self.redirect('/')

        for i in range(0, number):
            hacker = createTestHacker()
            hacker.put()
