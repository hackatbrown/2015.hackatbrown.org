import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib
import json
import logging
import hacker_page

class ChangeHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, secret, key):
        hacker = hacker_page.getHacker(secret)

        if hacker is None:
            logging.error("Attempted to change hacker's uploaded" + key + " but no hacker with key: " + secret)
            return self.redirect('/')

        existing = getattr(hacker, key)
        if existing:
            fileName = getFileName(existing)
            downloadLink = getDownloadLink(existing)

        files = self.get_uploads(key)
        if (len(files) > 0):
            newFile = files[0].key()
            if existing:
                blobstore.delete(existing)
            setattr(hacker, key, newFile)
            hacker_page.putHacker(hacker)
            downloadLink = getDownloadLink(newFile)
            fileName = getFileName(newFile)

        self.response.write(json.dumps({"success": True, "downloadLink": downloadLink, "fileName" : fileName}))

def getDownloadLink(blobKey):
    return '/__serve/' + str(blobKey)

def newURL(secret, key):
    return blobstore.create_upload_url('/secret/__change/' + secret + '/' + key)

def getFileName(blobKey):
    return blobstore.BlobInfo.get(blobKey).filename

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class NewURLHandler(webapp2.RequestHandler):
    def get(self, secret, key):
        url = newURL(secret, key);
        self.response.write(json.dumps({"newURL": url}))
