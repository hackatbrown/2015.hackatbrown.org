from google.appengine.api import mail
import pynliner
from html2text import HTML2Text

def send_email(html, subject, recipients):
	html = pynliner.fromString(html) # pynliner turns css stylesheets into inline styles, because gmail + other clients disallow style sheets
	plain_text = HTML2Text(html) # because we _must_ provide a plain-text alternative message body
	for recip in recipients:
		mail.send_mail(sender="HackAtBrown Robot <robot@hackatbrown.org>", to=recip, subject=subject, body=plain_text, html=html)
		print "MESSAGE:"
		print html.encode('utf-8')
