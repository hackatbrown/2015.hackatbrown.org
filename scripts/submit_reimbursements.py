import sys
import csv
import urllib
import urllib2

# Read CSV file
file = open('valid-reimbursements-1.csv')
students = csv.reader(file);

for student in students:

    # Construct Payload
    payload = {}

    payload["first_name"] = student[0].split(" ")[0]
    payload["last_name"] = student[0].split(" ")[1] if " " in student[0] else "None"
    payload["address1"] = student[4]
    if student[5] != "None":
        payload["address2"] = student[5] 
    payload["city"] = student[6]
    payload["state"] = student[7]
    if(student[8] != "None"):
        payload["zip"] = student[8]
    else:
        payload["zip"] = "N/A"
    payload["country"] = student[9]

    payload["email"] = "athyuttam_eleti@brown.edu"
    payload["phone"] = "4014993393"
    payload["department"] = "Computer Science: Hack@Brown"
    payload["Submit"] = "Submit"

    print payload

    # Submit Form
    url = 'https://secure.brown.edu/purchasing/visitor/'
    failedHTML = '<div class="submitted"><span>Please make sure that all required fields are filled in.</span></div>'

    form_data = urllib.urlencode(payload)
    req = urllib2.Request(url, form_data)
    result = urllib2.urlopen(req)
    result_page = result.read()

    # Print Status
    print student[1] + "," + str(not failedHTML in result_page)