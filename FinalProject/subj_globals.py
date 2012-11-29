from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import scipy.io
import cython
import datetime
import pickle

class Subject():
	"""
	Makes an Subject object with all of the data parameters and raw data.
	Includes method for writing to logfile
	"""

	def __init__(self, subj, block, elecs, srate, gdat, SJdir):
		#initialize variables
		self.subj = subj		#subject name (ie 'ST22')
		self.block = block		#block name (ie 'decision','target')
		self.elecs = elecs 		#what electrodes are good
		self.srate = srate		#data sampling rate
		self.gdat = gdat 		#raw data matrix elecs x tmpts (numpy array)
		self.SJdir = SJdir 		#subject directory (/DATA/Stanford/Subjs/)

		#create analysis and data folders (DO I NEED BOTH?)
		self.DTdir = os.path.join(self.SJdir, self.subj, 'data', self.block)
		if not os.path.isdir(self.DTdir):
			os.makedirs(self.DTdir) #recursive mkdir - will create entire path
			print 'making ' + self.DTdir

		#logfile creation
		self.logfile = os.path.join(self.DTdir, 'logfile.log')
		self.logit('created %s - %s' %(self.subj, self.block))

	def logit(self, message):
		logf = open(self.logfile, "a")
		logf.write('[%s] %s' % (datetime.datetime.now(), message))
		logf.flush()
		logf.close()

	def resample(self, srate_new=1000):
		"""
		Resamples srate to srate_new.
		"""
		#find rational fraction for resampling
		p, q = (srate_new / self.srate).as_integer_ratio()

		# NEED HELP installing upfirdn

		self.logit('resampled to %i' %(srate_new))

class Event(): #MAYBE MAKE IT A DICTIONARY?
	def __init__ (self, ANsrate, stimonset, stimoffset, responset, respoffset, badevent, resp, sample, cresp, SJdir):
		self.ANsrate = ANsrate		#analog sampling rate
		self.stimonset = stimonset 	#stim onset times (array)
		self.stimoffset = stimoffset
		self.responset = responset
		self.respoffset = respoffset
		self.badevent = badevent	#if the event is bad (array)
		self.resp = resp 			#subject responses (list)
		self.sample = sample 		#stimuli presented (array)
		self.cresp = cresp			#correct response (list)
		self.SJdir = SJdir 			#subject directory

		#create data folder (in case doesn't already exist)
		self.DTdir = os.path.join(self.SJdir, self.subj, 'data', self.block)
		if not os.path.isdir(self.DTdir):
			os.makedirs(self.DTdir) #recursive mkdir - will create entire path
			print 'making ' + self.DTdir
		
		#logfile creation
		self.logfile = os.path.join(self.DTdir, 'logfile.log')
		self.logit('created Events')

	def logit(self, message):
		logf = open(self.logfile, "a")
		logf.write('[%s] %s' % (datetime.datetime.now(), message))
		logf.flush()
		logf.close()

	def calc_acc(self):
		"""
		calculate subject accuracy per trial, store in Events, print mean acc
		"""
		self.acc = (self.resp == self.cresp).astype(int)
		print 'accuracy : %f' %(np.mean(self.acc))
		self.logit('calculated acc')
 
	def calc_RT(self):
		RT = np.round(np.subtract(self.responset,self.stimonset))
		good = np.flatnonzero(self.badevent == 0)
		self.RT = RT[good]
		print 'RT : %i ms' %(np.mean(self.RT)/self.ANsrate *1000)
		self.logit('calculated RT')

	def convert_srate(self,srate):
		"""
		converts the sampling rate to srate (and updates ANsrate)
		"""
		self.stimonset = round(self.stimonset / self.ANsrate * srate)
		self.stimoffset = round(self.stimoffset / self.ANsrate * srate)
		self.responset = round(self.responset / self.ANsrate * srate)
		self.respoffset = round(self.respoffset / self.ANsrate * srate)
		self.ANsrate = srate
		self.logit('resampled to %f, updated ANsrate' %(srate))


def save_dataobj(dataobj, directory, name): #gives memory error with pickle and cPickle - should reduce size?
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
