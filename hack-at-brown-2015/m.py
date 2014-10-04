import htmlmin # html minifier
import slimit # js minifier
import cssutils
import bs4
import urllib2
import urlparse
import wsgiref

class WSGIMiddleware:
	def __init__(self, app, memcache=None):
		self.app = app
		self.memcache = memcache

	def __call__(self, environ, start_response):
		if self.app.debug:
			return self.app(environ, start_response)
		content_type = ['application/octet-stream']
		def new_start_response(status, headers):
			for header, value in headers:
				if header == 'Content-Type':
					content_type[0] = value
			return start_response(status, headers)
		results = self.app(environ, new_start_response)
		content = "".join(results).decode('utf-8')
		base_url = wsgiref.util.request_uri(environ)
		m = Minifier(base_url)
		m.memcache = self.memcache
		return [m.minify(content, content_type[0]).encode('utf-8')]

class Minifier(object):
	memcache = None
	cache_time = 60 * 60
	def __init__(self, base_url=''):
		self.base_url = base_url

	def minify(self, _content, content_type):
		def _minify():
			content = _content
			if content_type.startswith('text/html'):
				soup = bs4.BeautifulSoup(content)
				self.inline_and_minify_js(soup)
				self.inline_and_minify_css(soup)
				content = unicode(soup)
				content = htmlmin.minify(content, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True, reduce_empty_attributes=True, reduce_boolean_attributes=True)
			elif content_type.startswith('text/javascript'):
				content = self.minified_js(content)
			elif content_type.startswith('text/css'):
				content = self.minified_css(content)
			return content
		return self.cached((_content + content_type).encode('utf-8'), _minify)

	def inline_and_minify_js(self, soup):
		for script in soup.find_all('script'):
			minify_this = not script.has_attr('no-minify')
			if script.has_attr('src'):
				if script.has_attr('no-inline'): continue
				url = urlparse.urljoin(self.base_url, script['src'])
				script_src = self.fetch_url(url).decode('utf-8')
				if url.endswith('.min.js'):
					minify_this = False
				script.clear()
				script.append(soup.new_string(script_src))
				del script['src']
			if minify_this:
				script_contents = u"".join(script.strings)
				script.clear()
				script.append(soup.new_string(self.minified_js(script_contents)))

	def minified_js(self, js):
		def _minified():
			return slimit.minify(js, mangle=False)
		return self.cached(js.encode('utf-8'), _minified)

	def inline_and_minify_css(self, soup):
		for style in soup.find_all('style'):
			if style.has_attr('no-minify'): continue
			content = u"".join(style.strings)
			content = self.minified_css(content)
			style.clear()
			style.append(soup.new_string(content))
		for link in soup.find_all('link', rel='stylesheet'):
			if link.has_attr('href') and not link.has_attr('no-inline'):
				css = self.fetch_url(urlparse.urljoin(self.base_url, link['href'])).decode('utf-8')
				content = css if link.has_key('no-minify') else self.minified_css(css)
				style_tag = soup.new_tag('style')
				style_tag.append(soup.new_string(content))
				link.replace_with(style_tag)

	def minified_css(self, css):
		def _minified():
			href = self.base_url if self.base_url != '' else None
			sheet = cssutils.parseString(css, href=href)
			sheet = cssutils.resolveImports(sheet)
			cssutils.ser.prefs.useMinified()
			return sheet.cssText
		return self.cached(css.encode('utf-8'), _minified)

	def cached(self, key, func):
		result = self.memcache.get(key) if self.memcache else None
		if not result:
			result = func()
		if self.memcache:
			try:
				self.memcache.add(key, result, self.cache_time)
			except Exception:
				pass
		return result

	def fetch_url(self, url):
		def _fetch():
			return urllib2.urlopen(url).read()
		return self.cached(url, _fetch)

