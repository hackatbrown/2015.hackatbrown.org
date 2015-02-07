import webapp2
from template import template
from messages import Message
from social_import import Post

class DayOfHandler(webapp2.RequestHandler):
	def get(self, tab='info'):
		params = {}

		params['bigboard'] = self.request.get('bigboard')
		
		if tab == 'info':
			feed = []
			for msg in Message.query(Message.show_in_day_of == True).order(-Message.added).fetch(limit=20):
				feed.append({"date": msg.added, "type": "message", "message": msg})
			for post in Post.query(Post.feed == 'twitter/user/HackAtBrown', Post.is_reply == False).order(-Post.date).fetch(limit=20):
				feed.append({"date": post.date, "type": "tweet", "tweet": post})
			feed.sort(key=lambda x: x['date'], reverse=True)
			params['feed'] = feed[:min(len(feed), 20)]
		

		content = template("day_of/{0}.html".format(tab), params) # TODO: security-ish stuff
		
		if self.request.get('ajax'):
			self.response.write(content)
		else:
			index_params = {
				"tab": tab,
				"tab_content": content,
				"bigboard": self.request.get('bigboard')
			}
			self.response.write(template("day_of/index.html", index_params))
