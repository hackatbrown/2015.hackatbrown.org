from google.appengine.api import mail
import pynliner
import html2text

def send_email(html, subject, recipients):
	html = pynliner.fromString(html) # pynliner turns css stylesheets into inline styles, because gmail + other clients disallow style sheets
	plain_text = html2text.html2text(html) # because we _must_ provide a plain-text alternative message body
	for recip in recipients:
		mail.send_mail(sender="HackAtBrown Robot <hello@hackatbrown.org>", to=recip, subject=subject, body=plain_text, html=html)
		print "MESSAGE:"
		print html.encode('utf-8')
