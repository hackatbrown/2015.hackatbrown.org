import jinja2, os
from jinja2 import utils

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def template(filename, vals={}):
	return JINJA_ENVIRONMENT.get_template(filename).render(vals)

def template_string(template, vals={}):
	return jinja2.Template(template).render(vals)
