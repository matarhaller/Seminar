from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import math
import scipy.io

class subj_globals():
	def __init__(self, subj, block, elecs, ANsrate, srate, gdat, SJdir):
		#initialize variables
		self.subj = subj		#subject name (ie 'ST22')
		self.block = block		#block name (ie 'decision','target')
		self.elecs = elecs 		#what electrodes are good
		self.ANsrate = ANsrate	#analog sampling rate
		self.srate = srate		#digital sampling rate
		self.gdat = gdat 		#raw data matrix elecs x tmpts (numpy array)
		self.SJdir = SJdir 		#subject directory (/DATA/Stanford/Subjs/)

		#create analysis and data folders (DO I NEED BOTH?)
		self.DTdir = os.path.join(self.SJdir, self.subj, 'data', self.block)
		self.ANdir = os.path.join(self.SJdir, self.subj, 'analysis', self.block)

		if not os.path.isdir(self.DTdir):
			os.makedirs(self.DTdir) #recursive mkdir - will create entire path
			print 'making ' + self.DTdir
		
		if not os.path.isdir(self.ANdir):
			os.makedirs(self.ANdir)
			print 'making ' + self.ANdir
		
	def create_CAR(self, grouping): #need to parallelize with cython. 
	#too big to have as method inside a class?
		""" 
		Create common average reference data matrix, add to class.
		Calcuates CAR from only good electrodes, removes CAR from all elecs
		INPUT:
			grouping -  size of groups to average 
						(noise can come in banks of 16 because of preamp)
						if noise isn't grouped, grouping = number of electrodes
		"""
		numelecs = min(self.gdat.shape) # number of electrodes
		chRank = np.zeros(numelecs) 
		chRank[self.elecs] = 1 # which electrodes are good
		Ngroups = math.ceil(self.elecs[-1]/grouping)

		# make lookup table of electrode groupings 
		# according to how plugged in on the preamp
		groups =np.array([x*np.ones(grouping) for x in np.arange(Ngroups)])
		groups = groups.flatten()

		# preallocate CAR
		gdat_CAR = self.gdat.copy() # numelecs X tmpts
		CAR = np.zeros((Ngroups, max(self.gdat.shape))) # Ngroups X tmpts
		CAR_all = np.zeros(max(self.gdat.shape)) # 1 X tmepts

		# subtract the mean from each electrode (including bad)
		# then sum gdat by group only for valid electrodes
		for e in self.elecs:
			gdat_CAR[e,:] = self.gdat[e,:] - np.mean(self.gdat[e,:]) 
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
		CAR_all = np.divide(CAR_all, len(self.elecs))

		# add grouped CAR to class
		self.gdat_CAR_group = gdat_CAR 

		# remove total CAR for all electrodes (ungrouped)
		for e in np.arange(numelecs):
			gdat_CAR[e,:] = gdat_CAR[e,:] - CAR_all

		# add ungrouped CAR to class
		self.gdat_CAR = gdat_CAR


def save_dataobj(dataobj):
	""" save the object to file to be read later"""
	filename = os.path.join(dataobj.DTdir, 'alldata.pk')
	with open (filename, 'wb') as output:
		pickle.dump(dataobj, output, pickle.HIGHEST_PROTOCOL)

SJdir = '/Users/matar/Documents/PyTest/'
subj = 'ST01'
block = 'test'
data = scipy.io.loadmat('/Users/matar/Documents/MATLAB/Knight/DATA/ST22/data/gdat.mat')
gdat = data['gdat']
ANsrate = 2.4414e04
srate = 3.0518e03
bad_elecs = np.array([4,9,11,12,13,17,22,23,29,40,47,48,51,52,53,61,63,65, 66, 68, 69, 70, 71, 77, 91, 92, 95, 96])
bad_elecs = bad_elecs-1 #make it 0 ordered
Enum  = np.arange(96) #96 elecs
elecs = np.setdiff1d(Enum,bad_elecs)