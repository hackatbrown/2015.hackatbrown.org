import webapp2
from template import template
from social_import import Post
import random
import datetime
from google.appengine.ext import ndb

class RaffleHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write(template("raffle.html", {"service": self.request.get('service')}))
	
	def post(self):
		service = self.request.get('service')
		params = {"result": True, "service": service}
		if service == 'twitter':
			post = draw_post('twitter/search/#hackatbrown')
			params['url'] = 'http://twitter.com/{0}/status/{1}'.format(post.poster, post.id)
			params['text'] = post.text
		else:
			post = draw_post('instagram/tag/hackatbrown')
			params['url'] = post.instagram_link
		params['name'] = post.poster
		self.response.write(template("raffle.html", params))

def draw_post(feed):
	after = datetime.datetime.now() - datetime.timedelta(days=3)
	q = Post.query(ndb.AND(Post.feed == feed, Post.date >= after))
	count = q.count()
	i = int(random.random() * count)
	print 'INDEX', i
	return q.fetch(offset=i, limit=1)[0]
