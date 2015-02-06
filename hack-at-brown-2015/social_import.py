import webapp2
from google.appengine.ext import ndb
from google.appengine.api import memcache
import twitter

"""
this class imports social feeds into the datastore, for a couple use cases:
- showing h@b official tweets on at.hackatbrown.org
- drawing random tweets (+ instagram photos later) using the h@b hashtag
"""

class Post(ndb.Model):
	feed = ndb.StringProperty()
	poster = ndb.StringProperty()
	text = ndb.TextProperty()
	image_url = ndb.TextProperty()
	date = ndb.DateTimeProperty()
	id = ndb.IntegerProperty()
	is_reply = ndb.BooleanProperty(default=False)

class Feed(object):
	def name(self):
		pass

	def update(self):
		pass

class TwitterFeed(Feed):
	def latest_id(self):
		posts = Post.query(Post.feed == self.name()).order(-Post.id).fetch(limit=1)
		return posts[0].id if posts else None

	def post_from_tweet(self, tweet):
		# find existing:
		existing = Post.query(Post.id == tweet.id).fetch(limit=1)
		if existing:
			return existing
		p = Post(id=tweet.id, 
			feed=self.name(), 
			date=tweet.created_at, 
			text=tweet.text, 
			poster=tweet.author.name,
			is_reply=tweet.in_reply_to_user_id_str != None)
		for image in tweet.entities.get('media', []):
			p.image_url = image['media_url']
		return p

	def update(self):
		posts = []
		for tweet in self.get_tweets():
			post = self.post_from_tweet(tweet)
			posts.append(post)
		ndb.put_multi(posts)

	def get_tweets(self):
		return []

class TwitterUserFeed(TwitterFeed):
	def __init__(self, user):
		self.user = user

	def get_tweets(self):
		return twitter.api.user_timeline(self.user, since_id=self.latest_id(), count=5)

	def name(self):
		return 'twitter/user/' + self.user

feeds = [TwitterUserFeed("HackAtBrown")]

class WorkHandler(webapp2.RequestHandler):
	def get(self):
		for feed in feeds:
			feed.update()
