import jinja2, os
from jinja2 import utils
import datetime

def day_of_date(date):
	""" a filter to convert dates into strings suitable for display on the day-of page"""
	utc_offset = datetime.timedelta(hours=-5)
	return (date - utc_offset).strftime('%A, %I:%M %p')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

JINJA_ENVIRONMENT.filters['day_of_date'] = day_of_date

def template(filename, vals={}):
	return JINJA_ENVIRONMENT.get_template(filename).render(vals)

def template_string(template, vals={}):
	return jinja2.Template(template).render(vals)
