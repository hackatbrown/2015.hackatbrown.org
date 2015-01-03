import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib
import json
import logging
import hacker_page
import operator

#Todo: shouldn't be called this.
class ChangeHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, secret, key):
        hacker = hacker_page.getHacker(secret)

        if hacker is None:
            logging.error("Attempted to change hacker's uploaded" + key + " but no hacker with key: " + secret)
            return self.redirect('/')

        #all repeated or big if statement
        existingFiles = getattr(hacker, key, [])
        newFiles = map(lambda f: f.key(), self.get_uploads(key))
        setattr(hacker, key, existingFiles + newFiles)
        hacker_page.putHacker(hacker)

        downloadLinks = map(getDownloadLink, newFiles)
        fileNames = getFileNames(newFiles)

        self.response.write(json.dumps({"downloadLinks": downloadLinks, "fileNames" : fileNames}))

def getDownloadLink(blobKey):
    return '/__serve/' + str(blobKey)

def newURL(secret, key):
    return blobstore.create_upload_url('/secret/__change/' + secret + '/' + key)



def getFileNames(blobKeys):
    if blobKeys is None:
        return None
    print(blobKeys)
    return map(lambda key: blobstore.BlobInfo.get(key).filename, blobKeys)

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class NewURLHandler(webapp2.RequestHandler):
    def get(self, secret, key):
        url = newURL(secret, key);
        self.response.write(json.dumps({"newURL": url}))
