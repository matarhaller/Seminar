import urllib2
import re
import numpy as np
import random

class Bear:
	"""
	HW 0 : Bear class 
	"""
	namecnt = 0
	idlist = 0
	dead = 0
	born = 0
	allnames = dict()
	allbears = dict()
	fertileMales = dict()
	fertileFemales = dict()
		
	def __init__(self,name):
		self.name = name
		self.age = 0
		self.id = Bear.idlist
		self.babies = list()
		self.numbabies = 0
		self.babyage = 0
		self.parents = ""
		self.death = round(np.random.normal(35, 5))
		Bear.idlist+=1
		Bear.born+=1
		Bear.allnames.update({self.id : self.name})
		Bear.allbears.update({self.id : self})
	
	def __del__(self,femalenames,malenames):
		Bear.allnames.update({self.id : self.name + ' - DECEASED'}) 
		Bear.allbears.pop(self.id) #remove from allbears list
		Bear.dead += 1
		#separating fertility by genders
		if self.sex == 1: #male
			malenames.append(self.name) #add name to end of list
			try:
				Bear.fertileMales.pop(self.id) #remove from fertile list
			finally:
				return
		else: #female
			femalenames.append(self.name) #add name to end of list
			try:
				Bear.fertileFemales.pop(self.id)
			finally:
				return
			
	def ageme(self):
		self.age += 1
		self.babyage += 1 # Time since last birth
	
	def isfertile(self):
		if (self.age > 4) and (self.babyage > 4):
			if self.sex == 1: #male
				Bear.fertileMales.update({self.id : self})
			else:
				Bear.fertileFemales.update({self.id : self})
			return True
		else: #remove from fertility list - if not removed already
			if self.sex == 1: #male
				try:
					Bear.fertileMales.pop(self.id)
				finally:
					return False
			else: #female
				try:
					Bear.fertileFemales.pop(self.id)
				finally:
					return False
		
	def procreate(self,mate,femalenames,malenames, pmale=50):
		choices = '1'*pmale+'0'*(100-pmale) #hack
		sex = int(random.choice(choices))
		if sex == 1: #male
			names = malenames
		else:
			names = femalenames
		baby = Bear(self.pickname(names))
		baby.sex = sex
		baby.parents = {self,mate} #unordered set
		self.babies.append(baby)
		self.numbabies += 1
		self.babyage = 0
		mate.babies.append(baby)
		mate.numbabies+=1
		mate.babyage = 0
		if self.sex == 1: #male
			Bear.fertileMales.pop(self.id) #remove from fertiles lists
			Bear.fertileFemales.pop(mate.id)
		else:
			Bear.fertileMales.pop(mate.id) 
			Bear.fertileFemales.pop(self.id)
		return baby

	def pickname(self,names):
		unique = 0
		while unique == 0:
			myname = names[Bear.namecnt]
			if myname != self.allnames.values:
				Bear.namecnt+=1 #move pointer
				unique = 1
			else:
				Bear.namecnt+=1 #go to next name
		return myname
	
	def findmatch(self):
		for cnt in range(100): #100 tries to find a mate
			if self.sex == 1: #male
				try:
					randid = np.random.randint(len(Bear.fertileFemales.keys()))
					mateid = Bear.fertileFemales.keys()[randid]
					mate = Bear.fertileFemales[mateid]
				except: #if there are no fertile bears of the other gender
					return False
			else: #female
				try:
					randid = np.random.randint(len(Bear.fertileMales.keys()))
					mateid = Bear.fertileMales.keys()[randid]
					mate = Bear.fertileMales[mateid]
				except:
					return False
			if (mate.parents != self.parents) and abs(self.age - mate.age<10):
				return mate
# Class Bear end

def listofnames(num,gender):
	names = list()
	if gender == 'f':
		g = 'feminine'
	else:
		g = 'masculine'				
	for j in range(num):
		#n = np.random.randint(20) #random page (out of 20 total)
		url = "http://listofnames.info/find.php?source=" + g + "&page="
		url+=str(j)
		site = urllib2.urlopen(url)
		s = site.read()
		site.close()		
		names.extend(re.findall('[A-Z][a-z]+\ [A-Z][a-z]+',s)) #thanks
	return names
		
class World:
	
	def __init__(self):
		femalenames = listofnames(20,'f')
		malenames = listofnames(20,'m')
	
		Adam = Bear("Adam")
		Adam.sex = 1
		Adam.parents = "God"
		Eve = Bear("Eve")
		Eve.sex = 0
		Eve.parents = "Adam's Rib"
		Mary = Bear("Mary")
		Mary.sex = 0
		Mary.parents = "Jesus's Grandparents"
	
	def runworld(self,numyears):
		for t in xrange(numyears):
			for b in Bear.allbears.values():
				b.ageme()
				if b.isfertile():
					mate = b.findmatch()
					if mate:
						b.procreate(mate,self.femalenames,self.malenames)
				if b.age >= b.death:
					b.__del__(self.femalenames,self.malenames)
		return (Bear.born, Bear.dead)
#end World
		
def answer_hw():
	"""Build a bear population over 150 years, starting from bear cubs named Adam, Eve, and Mary"""
	### a. On average, how many Bears are born in the first 100 years? How many Bears are alive at the end of 150 years?
	born, dead = World().runworld(100)
	avebirths = born

## This is what I would do if I was able to run my class >1 time
#	numruns = 3
#	allbirths = 0
#	worlds = []
#	for x in xrange(numruns): #average over numruns times
#		worlds.append(World())
#		born, dead = worlds[-1].runworld(100)
#		allbirths+= born
#	avebirths = allbirths/numruns
	
	print "question a"
	print "-"*50
	print "average number of Bears born in first 100 years: %i \n" % (avebirths)
	print "-"*50

## This is what I would do if I was able to run my class >1 time
#	alive = 0
#	worlds = []
#	for x in xrange(numruns):
#		worlds.append(World())
#		born, dead = worlds[-1].runworld(150)
#		alive += born-dead
#	avealive = alive/numruns
	
	print "question a continued"
	print "-"*50
	print "Bears alive at end of 150 years: %i \n" % (avealive)
	print "-"*50
	
	### b.What must be the minimum value of P(male) such that the population does not die out in 150 years?
	pmale = [10, 5, 1]
	for P in pmale:
		world(150)
		if Bear.dead == Bear.born:
			print "population not sustained with pmale = %i" % P
		else:
			print "population ok with pmale = %i" % P
	
	### c. Build and use a plotting routine to show the genealogy tree of a given Bear. Show all Bears at the same generation and earlier who are directly related.


#t = timeit.Timer(stmt ="world(100)",setup = "from __main__ import world")