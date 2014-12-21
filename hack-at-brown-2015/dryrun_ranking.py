from ranking2015 import *


class DummyApplicant:
	def __init__(self, ID=0):
		def prob(): return random.uniform(0.0, 1.0)
		self.id = ID
		self.shirt_gen = "M" if prob() < 0.625 else "W"
		self.school = "Brown University" if prob() < 0.3 else "Someother University"
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
	
	print "12: ", len(filter(lambda x: x.admit_priority == 12, applicants))
	print "24: ", len(filter(lambda x: x.admit_priority == 24, applicants))
	print "36: ", len(filter(lambda x: x.admit_priority == 36, applicants))
	print "48: ", len(filter(lambda x: x.admit_priority == 48, applicants))
	print "60: ", len(filter(lambda x: x.admit_priority == 60, applicants))