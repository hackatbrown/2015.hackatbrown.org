#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from template import template
import config
import dashboard
import email_list
import registration
from google.appengine.ext import blobstore
import background_work
import hacker_page
import short_urls
import m
from google.appengine.api import memcache

class IndexHandler(webapp2.RequestHandler):
    def get(self):
			variables = {
				"registration_status": config.registration_status()
			}
			if config.registration_status() == config.REGISTRATION_OPEN:
				variables['registration_post_url'] = blobstore.create_upload_url('/register')
			self.response.write(template("index.html", variables))

app = webapp2.WSGIApplication([
	    ('/', IndexHandler),
		('/sign_up_for_updates', email_list.SignUpForUpdatesHandler),
		('/register', registration.RegistrationHandler),
		('/__check_registered', registration.CheckRegistrationHandler),
		('/secret/(.+)', hacker_page.HackerPageHandler),
		('/__update_hacker/(.+)', hacker_page.HackerUpdateHandler),
		('/__get_dash_stats', dashboard.DashboardBackgroundHandler),
		('/__send_email', dashboard.SendEmail),
		('/__breakdown/(\w+)', dashboard.BreakdownHandler),
		('/dashboard', dashboard.DashboardHandler),
		('/__manual', dashboard.ManualRegistrationHandler),
		('/__lookup_hacker/(.+)', dashboard.LookupHackerHandler),
		('/__background_work', background_work.BackgroundWorkHandler), # called by a background job set up in cron.yaml
		('/create_short_url', short_urls.Create),
		('/(.+)', short_urls.Serve)
], debug=True)
#app = m.WSGIMiddleware(app, memcache=memcache)

