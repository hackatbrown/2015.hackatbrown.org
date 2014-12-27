from random import *
from ranking2015 import *


def prob(): return uniform(0.0, 1.0)

class DummyApplicant:
	def __init__(self, ID=0):
		self.id = ID
		self.shirt_gen = "W" if prob() < 0.23 else "M"
		
		if prob() < 0.19:
			self.school = "Brown University"
		elif prob() < 0.1:
			self.school = "Rhode Island School of Design"
		else:
			self.school = "Someother University"
		
		self.first_hackathon = "yes" if prob() < 0.34 else "no"
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



def test(numentrants=1400):
	"""Use this function to test the ranking procedure.
	Simulates a round of applicants with teams for ranking.
	Prints statistical information about the input entrants and output selected.
	"""
	target = 350
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
	print "           ################"
	print "           # DRY-RUN TEST #"
	print "           ################\n"
	print r"  [#Brown/RISD, %Women, %First time]"
	print ""
	print numentrants, "applicants:  [{0}, {1:.4f}, {2:.4f}]".format(*shallow_analyze(applicants, num_accept=numentrants))
	print "---------------------------------------"
	rank_applicants(applicants)
	print "first", target, "admits: [{0}, {1:.4f}, {2:.4f}]".format(*shallow_analyze(applicants, num_accept=target))
	print ""
	analyze(applicants, num_accept=target)





