from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import scipy.io
import cython
import datetime
import pickle

#TEST

class Subject():
	"""
	Makes an Subject object with all of the data parameters and raw data.
	Includes method for writing to logfile
	"""

	def __init__(self, subj, block, elecs, srate, ANsrate, gdat, SJdir, Events):
		#initialize variables
		self.subj = subj		#subject name (ie 'ST22')
		self.block = block		#block name (ie 'decision','target')
		self.elecs = elecs 		#what electrodes are good
		self.srate = srate		#data sampling rate
		self.srate = ANsrate		#analog sampling rate
		self.gdat = gdat 		#opened file of raw data matrix elecs x tmpts (numpy array) with pytables or hdf5. have 2 tables, 1 to write to, 1 to read from so not all contained in RAM - look in databases lecture. or db where each elec is a row in db. loop through each id and loop over it, pull out elec id .... hdf5 is db thing optimized for numerical work.
		self.SJdir = SJdir 		#subject directory (/DATA/Stanford/Subjs/)
		self.Events = Events	#dictionary of timing information

		#create analysis and data folders (DO I NEED BOTH?)
		self.DTdir = os.path.join(self.SJdir, self.subj, 'data', self.block)
		if not os.path.isdir(self.DTdir):
			os.makedirs(self.DTdir) #recursive mkdir - will create entire path
			print 'making ' + self.DTdir

		#logfile creation
		self.logfile = os.path.join(self.DTdir, 'logfile.log')
		self.logit('created %s - %s' %(self.subj, self.block))

	def logit(self, message):
		"""
		keep a log of all analyses done
		"""
		logf = open(self.logfile, "a")
		logf.write('[%s] %s' % (datetime.datetime.now(), message))
		logf.flush()
		logf.close()

	def resample(self, srate_new=1000):
		"""
		Resamples srate to srate_new. 
		Updates Events srate.

		"""
		#find rational fraction for resampling
		p, q = (srate_new / self.srate).as_integer_ratio()

		# NEED HELP installing upfirdn - email them, or find different resampling way.

		self.logit('resampled gdat from %f to %f' %(srate, srate_new))

		#for Events
		for k in self.Events.keys():
			if ismember(k, set('stimonset','stimoffset','responset','respoffset')):
				self.Events[k] = round(self.Events[k] / self.ANsrate * self.srate)
		self.logit('resampled Events from %f to %f' %(srate, srate_new))	
		
		#update srate, ANsrate
		self.srate = srate_new
		self.ANsrate = srate_new
		self.logit('update srate, ANsrate to %f' %(srate_new))

	def calc_acc(self):
		"""
		calculate subject accuracy per trial, store in Events, print mean acc
		"""
		self.Events['acc'] = (self.Events['resp'] == self.Events['cresp']).astype(int)
		print 'accuracy : %f' %(np.mean(self.Events['acc']))
		self.logit('calculated acc')
 
	def calc_RT(self):
		RT = np.round(np.subtract(self.Events['responset'],self.Events['stimonset']))
		good = np.flatnonzero(self.Events.['badevent'] == 0)
		self.Events['RT'] = RT[good]
		print 'RT : %i ms' %(np.mean(self.Events['RT'])/self.ANsrate *1000)
		self.logit('calculated RT')

	self.create_CAR = create_CAR #might need to be defined after create_CAR, or can just move create_CAR back inside.

def save_dataobj(dataobj, directory, name): 
	#gives memory error with pickle and cPickle - should reduce size?
	#different parameters assoc with each instantiation of class - with pointer to db.
	""" saves object to file to be read later
		INPUT: 
			dataobj - either Subject or Events
			directory - either DTdir (for Subject) or ANdir (for Events)
			filename without extension  - string, ex: subj + block or 'Events'
	"""
	fullfilename = os.path.join(directory, name + '.pkl')
	output = open(fullfilename, 'wb')
	pickle.dump(dataobj, output, -1)


def create_CAR(dataobj, grouping): 
	#too big to have as method inside a class?
	#to make less data - should overwrite the raw gdat with gdat_CAR, orig gdat will stay (outside of class)??
	# cython???

	""" 
	Create common average reference data matrix, add to class.
	Calcuates CAR from only good electrodes, removes CAR from all elecs
	INPUT:
		dataobj  -  from the Subject class
		grouping -  size of groups to average 
					(noise can come in banks of 16 because of preamp)
					if noise isn't grouped, grouping = number of electrodes
	"""
	numelecs = min(dataobj.gdat.shape) # total number of electrodes
	chRank = np.zeros(numelecs) 
	chRank[dataobj.elecs] = 1 # which electrodes are good
	Ngroups = math.ceil(dataobj.elecs[-1]/grouping)

	# make lookup table of electrode groupings 
	# according to how plugged in on the preamp
	groups =np.array([x*np.ones(grouping) for x in np.arange(Ngroups)])
	groups = groups.flatten()

	# preallocate CAR
	gdat_CAR = dataobj.gdat # numelecs X tmpts DONT DO COPY BC TOO MUCH DATA
	CAR = np.zeros((Ngroups, max(dataobj.gdat.shape))) # Ngroups X tmpts
	CAR_all = np.zeros(max(dataobj.gdat.shape)) # 1 X tmepts

	# pull three loops out into sep functions - only they will be in cython and compiled. write them in a separate file completely - in setup.py run them and compile them separately. can just feed it in the file object to the gdat or the filepath. in cython code can open the db and do for item in db. from comiled cython code import blah, on this file object/path do whatever.
	#write cython code (code.pyx) where do cdef to define function, run cython on it one time (definied in setup.py) - makes code.co file - then in here (python file) from code import function. now function is a python function (reads it in from code.so) or look at numexpr.
	# subtract the mean from each electrode (including bad)
	# then sum gdat by group only for valid electrodes
	for e in dataobj.elecs:
		gdat_CAR[e,:] = dataobj.gdat[e,:] - np.mean(dataobj.gdat[e,:]) 
		if chRank[e]: # valid elec
			CAR[groups[e],:] = CAR[groups[e],:] + gdat_CAR[e,:]

	# divide by number of valid elecs in each group (to get CAR per group)
	for cnt in np.arange(Ngroups):
		if np.sum(chRank[np.flatnonzero(groups == cnt)]): 
			#only if there is at least 1 valid elec in that group
			CAR[cnt,:] = np.divide(CAR[cnt,:], np.sum(chRank[np.flatnonzero(groups == cnt)]))

	# remove the relevant group CAR from each elec
	for e in np.arange(numelecs):
		gdat_CAR[e,:] = gdat_CAR[e,:] - CAR[groups[e],:]
		if chRank[e]:
			CAR_all = CAR_all + gdat_CAR[e,:] #sum CAR for valid elecs

	# calculate CAR for all elecs
	CAR_all = np.divide(CAR_all, len(dataobj.elecs))

	# add grouped CAR to class
	self.gdat_CAR_group = gdat_CAR 

	# remove total CAR for all electrodes (ungrouped)
	for e in np.arange(numelecs):
		gdat_CAR[e,:] = gdat_CAR[e,:] - CAR_all

	# add ungrouped CAR to class
	dataobj.gdat_CAR = gdat_CAR

	#log the change
	dataobj.logit('created CAR, grouping  = %i' %(grouping))
