import webapp2
from template import template
from messages import Message

class DayOfHandler(webapp2.RequestHandler):
	def get(self, tab='info'):
		params = {}
		
		if tab == 'info':
			params['messages'] = Message.query(Message.show_in_day_of == True).order(-Message.added).fetch(limit=20)
		
		content = template("day_of/{0}.html".format(tab), params) # TODO: security-ish stuff
		
		if self.request.get('ajax'):
			self.response.write(content)
		else:
			index_params = {
				"tab": tab,
				"tab_content": content
			}
			self.response.write(template("day_of/index.html", index_params))
