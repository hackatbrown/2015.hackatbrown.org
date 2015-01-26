import webapp2
from google.appengine.ext import ndb
from dashboard import getAllHackers
from registration import Hacker
from registration import generate_secret_for_hacker_with_email
import json
from template import template
from registration import hacker_keys
from config import isMasterDB
import random
from google.appengine.api import taskqueue
from config import isAdmin

#Example:
# json = {
#     "Rhode Island School of Design" : "Rhode Island School of Design"
#     "RISD" : "Rhode Island School of Design"
# }
# cleanup('school', json)
class CleanupHandler(webapp2.RequestHandler):
    def post(self):
        parsed_request = json.loads(self.request.body)
        property = parsed_request.get('property')
        jsonKeys = parsed_request.get('jsonKeys')
        result =  cleanup(property, jsonKeys)
        return self.response.write(json.dumps(result))

    def get(self):
        jinjaVars = {"properties" : hacker_keys}
        return self.response.write(template("db_cleanup.html", jinjaVars))

def cleanup(property, jsonKeys):
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
        if not isAdmin(): return self.redirect('/')

        if isMasterDB():
            return self.redirect('/')

        number = int(number)
        q = taskqueue.Queue('populate')

        def enqueue(start, end):
                params = {"start": start, "end" : end}
                q.add(taskqueue.Task(url='/dashboard/__db_populate/worker', params=params))

        start = 0
        end = 0
        batchSize = 40 #just copying nate

        for i in range(batchSize, number, batchSize):
            end = i
            enqueue(start, end)
            start = end

        if end < number:
            enqueue(end, number)

        self.response.write("Enqueued {0} hackers.".format(number))

class DepopulateHandler(webapp2.RequestHandler):
    def get(self, number):
        if not isAdmin(): return self.redirect('/')

        if isMasterDB():
            return self.redirect('/')

        number = int(number)

        ndb.delete_multi(
            Hacker.query().fetch(limit=number, keys_only=True)
        )
        self.response.write("Eliminated {0} hackers.".format(number))

class CreateTestHackerWorker(webapp2.RequestHandler):
    def post(self):
        if isMasterDB():
            return self.redirect('/')

        start = int(self.request.get('start'))
        end = int(self.request.get('end'))
        hackers = []
        for i in range(start, end):
            hackers.append(createTestHacker(i))

        ndb.put_multi(hackers)

def createTestHacker(number):

    shirts = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    def prob(): return random.uniform(0.0, 10.0)
    hacker = Hacker()
    hacker.name = "Hacker {0}".format(number)
    hacker.school = "Brown University" if prob() < 3 else "Another University"

    hacker.year = "freshman"
    if prob() < 3:
        hacker.year = "sophomore"
    elif prob() < 3:
        hacker.year = "junior"
    elif prob() < 3:
        hacker.year = "senior"

    hacker.email = "hacker_{0}@{1}.edu".format(number, hacker.school.lower().split(" ")[0])
    hacker.secret = generate_secret_for_hacker_with_email(hacker.email)

    hacker.shirt_gen = "M" if prob() < 5 else "W"
    hacker.shirt_size = random.choice(shirts)

    rawDiet = ["Vegetarian", "Vegan", "Gluten Free", "Kosher", "Lactose Intolerant", "Nuts Allergy", "Treenuts Allergy", "Soy Allergy",
"Shellfish Allergy", "Corn Allergy", "No Pork", "No Ham", "No Beef", "No Mutton", "Halal", "No Red Meat", "None"]
    drs = []
    while prob() < 2:
        item = random.choice(rawDiet)
        rawDiet.remove(item)
        drs.append(item)

    hacker.dietary_restrictions = ','.join(drs)

    tms = []
    while prob() < 2:
        tms.append("hacker_{0}@another.edu".format(random.randint(0, number)))

    hacker.teammates = ','.join(tms)

    hacker.hardware_hack = "yes" if prob() > 8 else "no"
    hacker.first_hackathon = "yes" if prob() > 7 else "no"

    def numberString(length):
        return ''.join(map(lambda x: str(random.randint(0, 9)), range(0, length)))

    hacker.phone_number = numberString(10)

    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    hacker.address1 = "Creative"
    hacker.address2 = "Address"
    hacker.city = "City"
    hacker.country = "Country"
    hacker.state = random.choice(states)
    hacker.zip = numberString(5)

    if hacker.school == "Another University":
        hacker.rmax = 1000
    else:
        hacker.rmax = 0

    hacker.rtotal = random.randint(0, hacker.rmax)

    return hacker
