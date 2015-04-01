import csv
import os
import requests

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

def dir_names_for_student_name(name):
	chars = 'abcdefghijklmnopqrtsuvwxyz'
	chars = chars + chars.upper() + ' 1234567890'
	name = ''.join([c for c in name if c in chars])
	yield name
	i = 1
	while True:
		yield name + ' ' + str(i)
		i += 1

def folder_for_name(name):
	for name in dir_names_for_student_name(name):
		path = os.path.join('receipts', name)
		if not os.path.exists(path):
			os.mkdir(path)
			return path

for hacker in csv.DictReader(open('receipts.csv')):
	urls = [x for x in hacker['receipt_urls'].split(" ") if len(x)]
	if len(urls):
		folder = folder_for_name(hacker['name'])
		for i, url in enumerate(urls):
			print folder
			print url
			r = requests.get(url)
			mime = r.headers.get('Content-Type', None)
			extension = ext_for_mime(mime)
			path = os.path.join(folder, 'receipt-' + str(i) + extension)
			print path
			f = open(path, 'wb')
			f.write(r.content)
			f.close()
			print '\n'
