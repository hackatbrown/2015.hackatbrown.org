from random import *
from ranking2015 import *


def prob(): return uniform(0.0, 1.0)

class DummyApplicant:
	def __init__(self, ID=0):
		self.id = ID
		self.shirt_gen = "W" if prob() < 0.23 else "M"
		
		if prob() < 0.22:
			self.school = "Brown University"
		elif prob() < 0.1:
			self.school = "RISD"
		else:
			self.school = "Someother University"
		
		self.first_hackathon = "yes" if prob() < 0.31 else "no"
		self.year = "freshman"
		if prob() < 0.3:
			self.year = "sophomore"
		elif prob() < 0.3:
			self.year = "junior"
		elif prob() < 0.3:
			self.year = "senior"
		self.admit_priority = 0
		self.teammates = []
		self.email = str(self.id) + "@brown.edu"



def test(numentrants=1000):
	"""Use this function to test the ranking procedure.
	Simulates a basic round of applicants for ranking.
	Prints statistical information about the input round and output selected.
	"""
	# Simulate Dummy Applicants
	applicants = [DummyApplicant(x) for x in range(numentrants)]
	# Simulate Dummy Teams
	for i,v in enumerate(applicants):
		while prob() < 0.25 and len(v.teammates) < 4:
			idx = randint(0, numentrants - 1)
			v.teammates.append(applicants[idx].email)
			if prob() < 0.65:
				applicants[idx].teammates.append(v.email)

	d0 = DummyApplicant(0)
	d0.shirt_gen = "W"
	d0.year = "sophomore"
	d0.first_hackathon = "no"
	d0.school = "Brown University"
	d0.email = "0@brown.edu"
	d0.teammates = ["1@brown.edu"]

	d1 = DummyApplicant(1)
	d1.shirt_gen = "M"
	d1.year = "sophomore"
	d1.first_hackathon = "yes"
	d1.school = "Brown University"
	d1.email = "1@brown.edu"
	d1.teammates = []

	d2 = DummyApplicant(2)
	d2.shirt_gen = "W"
	d2.year = "sophomore"
	d2.first_hackathon = "yes"
	d2.school = "Brown University"
	d2.email = "2@brown.edu"
	d2.teammates = ["0@brown.edu", "3@brown.edu", "4@brown.edu"]

	#applicants = [d0, d1, d2]

	# Simulate ranking
	print "\n\n"
	print r"# brown/risd, % female, % first time"
	print ""
	print numentrants, "applicants: ", analyze(applicants, num_accept=numentrants)
	print "----------------------------------------------"
	print "first", 350, "admits:", rank_applicants(applicants)
	print ""

	priorities = {}
	for a in applicants:
		if a.admit_priority in priorities:
			priorities[a.admit_priority] += 1
		else:
			priorities[a.admit_priority] = 1

	for k,v in sorted(priorities.items()):
		print v, ": ", k






