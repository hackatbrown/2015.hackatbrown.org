from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb

class Hacker(ndb.Model):
	name = ndb.StringProperty()
	school = ndb.StringProperty()
	year = ndb.StringProperty()
	email = ndb.StringProperty()
	shirt_size = ndb.StringProperty()
	dietary_restrictions = ndb.StringProperty()
	resume = ndb.BlobKeyProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

class RegistrationHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		hacker = Hacker()
		for key in ['name', 'school', 'year', 'email', 'shirt_size', 'dietary_restrictions']:
			setattr(hacker, key, self.request.get(key))
		resume_files = self.get_uploads('resume')
		if len(resume_files) > 0:
			hacker.resume = resume_files[0].key()
		hacker.put()
		self.redirect('/#thanks')
