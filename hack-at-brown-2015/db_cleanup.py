from google.appengine.ext import ndb
from dashboard import getAllHackers
import json

#Example:
# json = {
#     "Rhode Island School of Design" : "Rhode Island School of Design"
#     "RISD" : "Rhode Island School of Design"
# }
# run('school', json)

def run(property, jsonKeys):
    hackers = getAllHackers(property)
    numChanges = 0
    for hacker in hackers:
        currentProp = getattr(hacker, property)
        if currentProp and jsonKeys[currentProp] and currentProp != jsonKeys[currentProp]:
            try:
                setattr(hacker, jsonKeys[currentProp])
                hacker.put()
                numChanges++
            except Exception as err
                return self.response.write(json.dumps({"success":False, "msg": str(err.args[0])}))

    successMsg = "Changed the schools of " + numChanges + " hackers."
    return self.response.write(json.dumps({"success":True, "msg": successMsg}))
