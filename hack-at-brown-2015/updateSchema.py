import logging
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from registration import Hacker
import reimbursement

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def updateSchema(cursor=None, num_updated=0):
    to_put = []

    hackers, next_curs, more = Hacker.query().fetch_page(BATCH_SIZE, start_cursor=cursor)

    for hacker in hackers:
        append = False

        #Making sure nobody is admitted
        hacker.admitted_email_sent_date = None

        #Changing receipts to a repeated property
        if hacker.receipts is None or hacker.receipts == [None]:
            hacker.receipts = []
            append = True
        elif isinstance(hacker.receipts, ndb.BlobKeyProperty):
            receipt = hacker.receipts
            hacker.receipts = [receipt]
            append = True

        #Removing schools with whitespace around them.
        if hacker.school.strip() != hacker.school:
            hacker.school = hacker.school.strip()
            append = True

        #Creating the reimbursement max field
        if hacker.rmax == 0 or hacker.rmax is None:
            hacker.rmax = reimbursement.getMax(hacker.school)
            append = True

        if append:
            to_put.append(hacker)


    if to_put:
        ndb.put_multi(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            updateSchema, cursor=next_curs, num_updated=num_updated)
    else:
        logging.debug(
            'updateSchema complete with %d updates!', num_updated)
