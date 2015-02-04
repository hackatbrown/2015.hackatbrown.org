from csv import DictReader

hackers = [h for h in DictReader(open('resumes.csv')) if h.get('resume', 'None') != 'None']
from collections import defaultdict
hackers_with_names = defaultdict(int)

def strip_name(name):
	alphabet = 'abcdefghijklmnopqrstuvwxyz '
	return ''.join([c for c in name if c in alphabet + alphabet.upper()])

for hacker in hackers:
	name = strip_name(hacker['name'])
	extra = ''
	if hackers_with_names[name] > 0:
		extra = str(hackers_with_names[name] + 1)
	hacker['filename'] = name + extra
	hackers_with_names[name] += 1

from mimetypes import MimeTypes
mimetypes = MimeTypes()

def ext_for_mime(mime):
	if not mime: return ''
	explicit = {
		"application/msword": ".doc",
		"application/octet-stream": ""
	}
	if mime in explicit: return explicit[mime]
	ext = mimetypes.guess_extension(mime)
	return ext if ext else ''

from multiprocessing import Pool

import requests

def download_hacker(hacker):
	r = requests.get(hacker['resume'])
	mime = r.headers.get('Content-Type', None)
	extension = ext_for_mime(mime)
	print mime, extension
	filename = 'Hack at Brown Resumes/' + hacker['filename'] + extension
	f = open(filename, 'wb')
	f.write(r.content)
	f.close()

Pool(7).map(download_hacker, hackers)