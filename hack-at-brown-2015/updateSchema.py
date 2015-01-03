import logging
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from registration import Hacker

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def updateSchema(cursor=None, num_updated=0):
    query = Hacker.query()
    to_put = []
    for hacker in query.fetch(limit=BATCH_SIZE, start_cursor=cursor):
        if hacker.receipts is None or hacker.receipts == [None]:
            hacker.receipts = []
            to_put.append(hacker)
        elif isinstance(hacker.receipts, ndb.BlobKeyProperty):
            receipt = hacker.receipts
            hacker.receipts = [receipt]
            to_put.append(hacker)
        elif isinstance(hacker.receipts, list):
            continue

    if to_put:
        ndb.put_multi(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            updateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'updateSchema complete with %d updates!', num_updated)
