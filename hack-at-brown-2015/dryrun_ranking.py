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
	Simulates a basic round of applicants for ranking.
	Prints statistical information about the input round and output selected.
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
	print r"(# brown/risd, % women, % first time)"
	print ""
	print numentrants, "applicants: ", analyze(applicants, num_accept=numentrants)
	print "----------------------------------------------"
	print "first", 350, "admits:", rank_applicants(applicants)
	print ""

	priorities = {}
	for a in applicants:
		priorities[a.admit_priority] = priorities.get(a.admit_priority, 0) + 1

	for k,v in sorted(priorities.items()):
		print k, ": ", v

	for k,v in sorted(priorities.items()):
		print "\n\n----------{ rank", k, "stats }----------"

		apps = filter(lambda x: x.admit_priority == k, applicants)
		print "from", v, "applicants: ({0}, {1:1.3f}, {2:1.3f})".format(*analyze(apps, v))

		print "\nBrown/RISD women:", len(filter(lambda x: (x.school == "Brown University" or x.school == "Rhode Island School of Design") and x.shirt_gen == "W", apps))
		print "Brown/RISD men:  ", len(filter(lambda x: (x.school == "Brown University" or x.school == "Rhode Island School of Design") and x.shirt_gen == "M", apps))
		
		print "\nOther U women:", len(filter(lambda x: x.school != "Brown University" and x.school != "Rhode Island School of Design" and x.shirt_gen == "W", apps))
		print "Other U men:  ", len(filter(lambda x: x.school != "Brown University" and x.school != "Rhode Island School of Design" and x.shirt_gen == "M", apps))
		
		print "\nBrown/RISD first hackathon:", len(filter(lambda x: (x.school == "Brown University" or x.school == "Rhode Island School of Design") and x.first_hackathon == "yes", apps))
		print "Other U first hackathon:   ", len(filter(lambda x: x.school != "Brown University" and x.school != "Rhode Island School of Design" and x.first_hackathon == "yes", apps))

	print "\n"
	fill = 0
	idx = 0
	spriorities = sorted(priorities.items(), reverse=True)
	while fill < target:
		fill += spriorities[idx][1]
		idx += 1
		
	print "Cuttoff in rank {0} (higher ranks all accepted)".format(spriorities[idx][0])
	print r"(# brown/risd, % women, % first time)"





