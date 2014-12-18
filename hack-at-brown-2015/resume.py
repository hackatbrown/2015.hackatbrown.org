import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib
import json
import logging
import hacker_page

class ChangeHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, secret):
        hacker = hacker_page.getHacker(secret)

        if hacker is None:
            logging.error("Attempted to change hacker's uploaded resume but no hacker with key: " + secret)
            return self.redirect('/')

        resume_files = self.get_uploads('resume')
        if (len(resume_files) > 0):
            print(resume_files)
            newResume = resume_files[0].key()
            if hacker.resume:
                blobstore.delete(hacker.resume)
            hacker.resume = newResume

        hacker_page.putHacker(hacker)

        downloadLink = getDownloadLink(hacker)
        fileName = getFileName(hacker.resume)

        self.response.write(json.dumps({"success": True, "downloadLink": downloadLink, "fileName" : fileName}))

def getDownloadLink(hacker):
    return '/__serve/' + str(hacker.resume)

def newURL(secret):
    return blobstore.create_upload_url('/secret/__change/' + secret)

def getFileName(blobKey):
    return blobstore.BlobInfo.get(blobKey).filename

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class NewURLHandler(webapp2.RequestHandler):
    def get(self, secret):
        url = newURL(secret);
        self.response.write(json.dumps({"newURL": url}))
