import webapp2
import template
import registration

class HackerPageHandler(webapp2.RequestHandler):
    def get(self, secret):
        hacker = registration.Hacker.WithSecret(secret)

        if hacker is None:
            self.redirect('/')

        status = computeStatus(hacker)
        self.response.write(template.template("hacker_page.html", {"hacker": hacker, "status": status}))

def computeStatus(hacker):
    if hacker is None:
        return "Not Found"

    if hacker.checked_in == True:
        return "Checked In"
    elif hacker.rsvpd == True:
        return "RSVP'd"
    elif hacker.admitted_email_sent_date != None:
        return "Registered"
    elif hacker.waitlist_email_sent_date != None:
        return "Waitlisted"
    else:
        return "Not Currently Admitted"
