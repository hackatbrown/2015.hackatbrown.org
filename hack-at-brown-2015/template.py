import jinja2, os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def template(filename, vals={}):
	return JINJA_ENVIRONMENT.get_template(filename).render(vals)
