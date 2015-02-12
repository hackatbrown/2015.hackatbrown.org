import jinja2, os
from jinja2 import utils
import datetime
from autolink import linkify
import cgi

def day_of_date(date):
	""" a filter to convert dates into strings suitable for display on the day-of page"""
	offset = datetime.timedelta(hours=-5)
	return (date + offset).strftime('%A, %I:%M %p')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

JINJA_ENVIRONMENT.filters['day_of_date'] = day_of_date
JINJA_ENVIRONMENT.filters['linkify'] = lambda text: linkify(cgi.escape(text))

def template(filename, vals={}):
	return JINJA_ENVIRONMENT.get_template(filename).render(vals)

def template_string(template, vals={}):
	return jinja2.Template(template).render(vals)
