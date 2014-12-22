from ranking2015 import *


class DummyApplicant:
	def __init__(self, ID=0):
		def prob(): return random.uniform(0.0, 1.0)
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
		self.email = "blah@brown.edu"



def test(numentrants=1000):
	"""Use this function to test the ranking procedure.
	Simulates a basic round of applicants for ranking.
	Prints statistical information about the input round and output selected.
	"""
	applicants = [DummyApplicant(x) for x in range(numentrants)]

	print ""
	print r"# brown/risd, % female, % first time"
	print analyze(applicants, num_accept=numentrants)
	print "----------------------------------"
	print rank_applicants(applicants)
	

	priorities = {}
	for a in applicants:
		if a.admit_priority in priorities:
			priorities[a.admit_priority] += 1
		else:
			priorities[a.admit_priority] = 1

	for k,v in sorted(priorities.items()):
		print v, ": ", k

	print 
