import webapp2
from google.appengine.ext import ndb
from dashboard import getAllHackers
from registration import Hacker
from registration import generate_secret_hacker_with_email
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
            hacker = createTestHacker(i)


def createTestHacker(number):
    shirts = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    def prob(): return random.uniform(0.0, 10.0)
    hacker = Hacker()
    hacker.name = "Hacker {1}".format(number)
    hacker.school = "Brown University" if prob() < 3 else "Another University"

    hacker.year = "freshman"
    if prob() < 3:
        hacker.year = "sophomore"
    elif prob() < 3:
        hacker.year = "junior"
    elif prob() < 3:
        hacker.year = "senior"

    hacker.email = "hacker_{1}@{2}.edu".format(number, hacker.school.lower().split(" ")[0])
    hacker.secret = generate_secret_hacker_with_email(hacker.email)

    hacker.shirt_gen = "M" if prob() < 5 else "W"
    hacker.shirt_size = random.choice(shirts)

    rawDiet = ["Vegetarian", "Vegan", "Gluten Free", "Kosher", "Lactose Intolerant", "Nuts Allergy", "Treenuts Allergy", "Soy Allergy",
"Shellfish Allergy", "Corn Allergy", "No Pork", "No Ham", "No Beef", "No Mutton", "Halal", "No Red Meat", "None"]
    drs = []
    while prob() < 2:
        item = random.choice(rawDiet)
        rawDiet.remove(item)
        drs.push(item)

    hacker.dietary_restrictions = ','.join(drs)

    tms = []
    while prob() < 2:
        teammates.push("hacker_{1}@another.edu".format(randint(0, number)))

    hacker.hardware_hack = "yes" if prob() > 8 else "no"
    hacker.first_hackathon = "yes" if prob() > 7 else "no"

    hacker.put()

    return hacker
