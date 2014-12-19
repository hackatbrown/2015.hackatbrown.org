from google.appengine.ext import ndb
from dashboard import getAllHackers


#import json something like this
{
    "Rhode Island School of Design" : "Rhode Island School of Design"
    "RISD" : "Rhode Island School of Design"
}


def run(property, json):
    hackers = getAllHackers(property)
    for hacker in hackers:
        currentProp = getattr(hacker, property)
        if currentProp and json[currentProp]:
            try:
                setattr(hacker, json[currentProp])
                hacker.put()
            except Exception

