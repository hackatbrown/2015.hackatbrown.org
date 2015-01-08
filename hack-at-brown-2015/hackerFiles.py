import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib
import json
import logging
from hacker_page import putHacker, getHacker
import operator

#Todo: shouldn't be called this.
class ChangeHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, secret, key):
        hacker = hacker_page.getHacker(secret)

        if hacker is None:
            logging.error("Attempted to change hacker's uploaded" + key + " but no hacker with key: " + secret)
            return self.redirect('/')

        newFiles = map(lambda f: f.key(), self.get_uploads(key))
        multipleFileUpload = self.request.get('multiple') == "true"

        if multipleFileUpload:
            existingFiles = getattr(hacker, key, [])
            value = existingFiles + newFiles
        elif len(newFiles) > 0:
            existingFile = getattr(hacker, key, None)
            if existingFile:
                blobstore.delete(existingFile)
            value = newFiles[0]
        else:
            value = None

        setattr(hacker, key, value)
        hacker_page.putHacker(hacker)

        downloadLinks = map(getDownloadLink, newFiles)
        fileNames = getFileNames(newFiles)

        self.response.write(json.dumps({"downloadLinks": downloadLinks, "fileNames" : fileNames}))

def getDownloadLink(blobKey):
    return '/__serve/' + str(blobKey)

def newURL(secret, key):
    return blobstore.create_upload_url('/secret/__change/' + secret + '/' + key)

class DeleteFileHandler(webapp2.RequestHandler):
    def post(self, secret):
        hacker = hacker_page.getHacker(secret)

        if hacker is None:
            logging.error("Attempted to change hacker's uploaded" + key + " but no hacker with key: " + secret)
            return self.response.write("failure")

        key = self.request.get('key')
        files = getattr(hacker, key, [])
        files.remove(self.request.get('blobKey'))
        setattr(hacker, key, files)

        blobstore.delete(self.request.get('blobKey'))
        hacker_page.putHacker(hacker)

def getFileName(blobKey):
    if blobKey is None:
        return None
    info = blobstore.BlobInfo.get(blobKey)
    if info is None:
        return None

    return info.filename

def getFileNames(blobKeys):
    if blobKeys is None:
        return None
    return map(getFileName, blobKeys)

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class NewURLHandler(webapp2.RequestHandler):
    def get(self, secret, key):
        url = newURL(secret, key);
        self.response.write(json.dumps({"newURL": url}))
