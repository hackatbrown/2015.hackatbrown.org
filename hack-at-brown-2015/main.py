#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#			http://www.apache.org/licenses/LICENSE-2.0
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
import hackerFiles
import dashboard
import email_list
import registration
from google.appengine.ext import blobstore
import background_work
import hacker_page
import volunteer_reg
import db_utils
import short_urls
import m
import messages
import ranking2015
import csv_export
import day_of
import partner
import rewriter
import mentor
import csv_import
import social_import
import raffle
from google.appengine.api import users

class IndexHandler(webapp2.RequestHandler):
		def get(self):
			variables = {
				"registration_status": config.registration_status()
			}
			if config.registration_status() == config.REGISTRATION_OPEN:
				variables['registration_post_url'] = blobstore.create_upload_url('/register')
			self.response.write(template("index.html", variables))

class SecretIndexHandler(webapp2.RequestHandler):
		def get(self):
			variables = {
				"registration_status": "registration_open"
			}

			variables['registration_post_url'] = blobstore.create_upload_url('/register')
			self.response.write(template("index.html", variables))

def static_page_handler(html_file):
	class Handler(webapp2.RequestHandler):
		def get(self):
			self.response.write(template(html_file))
	return Handler

class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url('/'))

app = webapp2.WSGIApplication([
	    ('/', IndexHandler),
	    ('/sponsor-dashboard', partner.PartnerPageHandler),
	    ('/__partner_csv',partner.PartnerCSVDownload),
		('/sign_up_for_updates', email_list.SignUpForUpdatesHandler),
		('/register', registration.RegistrationHandler),
		('/__check_registered', registration.CheckRegistrationHandler),
		('/secret/__change/([^\/]+)/(.+)', hackerFiles.ChangeHandler),
		('/secret/__rsvp/(.+)', hacker_page.RSVPHandler),
		('/secret/__newurl/([^\/]+)/(.+)', hackerFiles.NewURLHandler),
		('/secret/__delete_file/(.+)', hackerFiles.DeleteFileHandler),
		('/secret/(.+)', hacker_page.HackerPageHandler),
		('/__update_hacker/(.+)', hacker_page.HackerUpdateHandler),
		('/__delete_hacker/(.+)', hacker_page.DeleteHackerHandler),
		('/__serve/([^/]+)?', hackerFiles.ServeHandler),
		('/dashboard/__get_dash_stats', dashboard.DashboardBackgroundHandler),
		('/dashboard/__breakdown/(\w+)', dashboard.BreakdownHandler),
		('/dashboard/__breakdown/(\w+)/(\w+)', dashboard.FilteredBreakdownHandler),
		('/dashboard', dashboard.DashboardHandler),
		('/dashboard/messages', messages.MessagesDashboardHandler),
		('/dashboard/messages/message_task_queue_work', messages.MessagesTaskQueueWork),
		('/dashboard/normalize_emails', dashboard.NormalizeEmailsHandler),
		('/dashboard/ranking', dashboard.RankingDashHandler),
		('/dashboard/__rank', ranking2015.RankingHandler),
		('/dashboard/__manual', dashboard.ManualRegistrationHandler),
		('/dashboard/__lookup_hacker/(.+)', dashboard.LookupHackerHandler),
		('/dashboard/db_cleanup', db_utils.CleanupHandler),
		('/dashboard/__db_populate/(\d+)', db_utils.PopulateHandler),
		('/dashboard/__db_populate/worker', db_utils.CreateTestHackerWorker),
		('/dashboard/__db_depopulate/(\d+)', db_utils.DepopulateHandler),
		('/dashboard/__cleanup', db_utils.CleanupHandler),
        ('/dashboard/csv', csv_export.CsvExport),
        ('/dashboard/register', SecretIndexHandler),
		('/dashboard/volunteer_registration', volunteer_reg.VolunteerRegistrationHandler),
		('/dashboard/upload_csv', csv_import.ImportPageHandler),
		('/dashboard/volunteer_confirmation', volunteer_reg.VolunteerConfirmationHandler),
		('/dashboard/mentor_dispatch', mentor.DispatchHandler),
		('/dashboard/mentor_dispatch/request/(.+)', mentor.ViewRequestHandler),
		('/dashboard/mentor_dispatch/get_requests', mentor.GetRequestsHandler),
		('/dashboard/mentor_dispatch/unpair', mentor.ResponseFinishedHandler),
		('/dashboard/mentor_dispatch/assigned', mentor.GetAssignedHandler),
		('/__background_work', background_work.BackgroundWorkHandler), # called by a background job set up in cron.yaml
		('/dayof', day_of.DayOfHandler),
		('/dayof/mentor_request', mentor.MentorRequestHandler),
		('/dayof/([a-z]+)', day_of.DayOfHandler),
		('/create_short_url', short_urls.Create),
		('/goodbye', static_page_handler("goodbye.html")),
		('/mentor', mentor.MentorSignupHandler),
		('/__social_import', social_import.WorkHandler),
		('/dashboard/raffle', raffle.RaffleHandler),
		('/logout', LogoutHandler),
		('/(.+)', short_urls.Serve)
], debug=True)
#app = m.WSGIMiddleware(app, memcache=memcache)
app = rewriter.WSGIMiddleware(app) # rewrite at.hackatbrown.org/xyz -> hackatbrown.org/dayof/xyz (also hackatbrown.org/xyz?dayof -> hackatbrown.org/dayof/xyz)
