from random import *
from ranking2015 import *


def prob(): return uniform(0.0, 1.0)

class DummyApplicant:
	def __init__(self, ID=0):
		self.id = ID
		self.shirt_gen = "M" if prob() < 0.625 else "W"
		
		if prob() < 0.25:
			self.school = "Brown University"
		elif prob() < 0.1:
			self.school = "RISD"
		else:
			self.school = "Someother University"
		
		self.first_hackathon = "yes" if prob() < 0.35 else "no"
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

	# Simulate ranking
	print "\n\n"
	print r"# brown/risd, % female, % first time"
	print ""
	print "applicants:      ", analyze(applicants, num_accept=numentrants)
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

