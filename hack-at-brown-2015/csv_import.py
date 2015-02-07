import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import models
import mentor
import logging
import re

class ImportPageHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/dashboard/upload_csv')

        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <select name="kind">
        <option value="Mentor">Mentor</option>
        </select>
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url

        self.response.write(html_string)

    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        kind = self.request.get('kind')
        blob_info = upload_files[0]
        process_csv(blob_info, kind)

        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")


def process_csv(blob_info, kind):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter=',')
    headers = reader.next()
    for row in reader:
        person = dict(zip(headers, row))
        if kind == "Mentor":
            create_mentor(person)

def create_volunteer(person):
    vol = models.Volunteer()
    vol.name = person['Name']
    vol.email = person['Email']
    gen, size = person['T-shirt Size'].split('-')
    vol.shirt_gen = gen
    vol.shirt_size = size
    pn = re.sub('[^\d]', '', person['Phone Number'])
    if pn:
        vol.phone_number = pn

    #TODO - role?
    vol.put()

def create_mentor(person):
    m = mentor.Mentor()

    existing = models.Rep.query(models.Rep.email = person['Email Address']).fetch()

    if not existing:
        pn = re.sub('[^\d]', '', person['Phone Number'])
    else:
        pn = existing.phone_number

    m.phone = pn
    m.email = person['Email Address']
    m.name = person['Name']
    m.tags = person['Skills or Experience'].split(', ')
    m.role = person['Role at Company']
    m.availability = '?'
    m.details = '?'
    m.put()


def create_rep(person):
    rep = models.Rep()
    rep.name = person['Name']
    rep.email = person['Email Address']
    pn = re.sub('[^\d]', '', person['Phone Number'])
    if pn:
        rep.phone_number = pn
    rep.company = person['Company']

    mensShirt = person["T-Shirt Size [Men's]"]
    womensShirt = person["T-Shirt Size [Women's]"]

    if mensShirt in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
        rep.shirt_gen = 'M'
        rep.shirt_size = mensShirt
    elif womensShirt in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
        rep.shirt_gen = 'M'
        rep.shirt_size = womensShirt

    rep.put()
