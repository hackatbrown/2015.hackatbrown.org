import webapp2
import template
import registration

class HackerPageHandler(webapp2.RequestHandler):
	def get(self, secret):
		hacker = registration.Hacker.WithSecret(secret)
		self.response.write(template.template("hacker_page.html", {"hacker": hacker}))
