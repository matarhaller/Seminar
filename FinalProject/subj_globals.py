from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import scipy.io
import cython
import datetime
import cPickle
import upfirdn
import h5py

def create_CAR(dataobj, grouping): 
	# cython???
	""" 
	Create common average reference data matrix, add to class.
	Calcuates CAR from only good electrodes, removes CAR from all elecs
	Adds subgroups to gdat hdf5 file - so can only be run once (becuase can't overwrite subgroups without first deleting them)

	INPUT:
		dataobj  -  from the Subject class
		grouping -  size of groups to average 
					(noise can come in banks of 16 because of preamp)
					if noise isn't grouped, grouping = number of electrodes
	"""
	#load in gdat data
	f = h5py.File(dataobj.gdat,'a')
	gdat = f['gdat']

	# define size parameters
	numelecs = min(gdat.shape) # total number of electrodes
	chRank = np.zeros(numelecs) 
	chRank[dataobj.elecs] = 1 # which electrodes are good
	Ngroups = math.ceil(dataobj.elecs[-1]/grouping)

	# preallocate gdat_CAR, CAR, CAR_all, gdat_CAR_group
	# add to gdat file as subgroups
	subgroup = f.create_group("CAR")
	gdat_CAR = subgroup.create_dataset('gdat_CAR', data = gdat)
	CAR = subgroup.create_dataset('CAR', shape = (Ngroups, max(gdat.shape)), dtype = gdat.dtype)
	CAR_all = subgroup.create_dataset('CAR_all', shape = (1, max(gdat.shape)), dtype = gdat.dtype)

	# make lookup table of electrode groupings 
	# according to how plugged in on the preamplifier during recording
	groups =np.array([x*np.ones(grouping) for x in np.arange(Ngroups)])
	groups = groups.flatten()

	# pull three loops out into sep functions - only they will be in cython and compiled. write them in a separate file completely - in setup.py run them and compile them separately. can just feed it in the file object to the gdat or the filepath. in cython code can open the db and do for item in db. from comiled cython code import blah, on this file object/path do whatever.
	#write cython code (code.pyx) where do cdef to define function, run cython on it one time (definied in setup.py) - makes code.co file - then in here (python file) from code import function. now function is a python function (reads it in from code.so) or look at numexpr.

	# subtract the mean from each electrode (including bad)
	# then sum gdat by group only for valid electrodes
	for e in dataobj.elecs:
		gdat_CAR[e,:] = gdat[e,:] - np.mean(gdat[e,:]) 
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

	# add grouped CAR to class (without removing total CAR for all elecs)
	gdat_CAR_group = gdat_CAR 

	# remove total CAR for all electrodes (ungrouped)
	for e in np.arange(numelecs):
		gdat_CAR[e,:] = gdat_CAR[e,:] - CAR_all

	#close file
	f.close()

	#log the change
	dataobj.logit('created CAR - grouping  = %i\nadded to %s' %(grouping, dataobj.gdat))

class Subject():
	"""
	Makes an Subject object with all of the data parameters and raw data.
	Includes method for writing to logfile
	"""
	def __init__(self, subj, block, elecs, srate, DTdir, Events):
		#initialize variables
		self.subj = subj			#subject name (ie 'ST22')
		self.block = block			#block name (ie 'decision','target')
		self.elecs = elecs 			#what electrodes are good
		self.srate = srate			#data sampling rate
		self.DTdir = DTdir 			#subject directory (/DATA/Stanford/Subjs/)
		self.Events = Events		#dictionary of timing information

		#logfile creation
		self.logfile = os.path.join(self.DTdir, 'logfile.log')
		self.logit('created %s - %s' %(self.subj, self.block))

		self.create_CAR = create_CAR #common ave ref method (defined above)
		self.gdat = os.path.join(DTdir, 'gdat.hdf5') #filepath to hdf5 file containing raw data

	def logit(self, message):
		"""
		keep a log of all analyses done
		"""
		logf = open(self.logfile, "a")
		logf.write('\n[%s] %s\n' % (datetime.datetime.now(), message))
		logf.flush()
		logf.close()

	def resample(self, srate_new=1000): #NEED TO DO USING UPFIRDN
		"""
		Resamples srate to srate_new. 
		Updates Events ANsrate.
		"""
		#find rational fraction for resampling
		p, q = (srate_new / self.srate).as_integer_ratio()

		#INSERT UPFIRDN HERE

		self.logit('resampled gdat from %f to %f' %(srate, srate_new))

		#for Events
		for k in self.Events.keys():
			if ismember(k, set('stimonset','stimoffset','responset','respoffset')):
				self.Events[k] = round(self.Events[k] / self.Events['ANsrate'] * srate_new)
		self.logit('resampled Events from %f to %f' %(Events['ANsrate'], srate_new))
		
		#update srate, ANsrate
		self.srate = srate_new
		Events['ANsrate'] = srate_new
		self.logit("update self.srate, Events['ANsrate'] to %f" %(srate_new))

	def calc_acc(self):
		"""
		calculate subject accuracy per trial, store in Events, print mean acc
		drops ambiguous stimuli from calculation
		"""
		good = self.Events['badevent']== 0
		notambig = self.Events['cresp'] != 'u'

		trials = np.flatnonzero(good & notambig)

		self.Events['acc'] = (self.Events['resp'][trials] == self.Events['cresp'][trials]).astype(int)
		
		print 'accuracy : %f' %(np.mean(self.Events['acc']))
		self.logit('calculated acc - %f' %(np.mean(self.Events['acc'])))
 
	def calc_RT(self):
		RT = np.round(np.subtract(self.Events['responset'],self.Events['stimonset']))
		good = np.flatnonzero(self.Events['badevent'] == 0)
		self.Events['RT'] = RT[good]
		print 'RT : %i ms' %(np.mean(self.Events['RT'])/self.Events['ANsrate'] *1000)
		self.logit('calculated RT - %f ms' %(np.mean(self.Events['RT']/self.Events['ANsrate']*1000)))

	def save_dataobj(self): 
		""" 
		pickles object to file to be read later from DTdir
		"""
		fullfilename = os.path.join(self.DTdir, (self.subj + '_' + self.block + '.pkl'))
		output = open(fullfilename, 'wb')
		cPickle.dump(self, output, -1)
		output.close()
		self.logit('saved %s' %(fullfilename))

#start up functions
def make_datafile(pathtodata, DTdir):
	"""
	make hdf5 data file and its encompassing data folder (DTdir)
	this function will only run once
	INPUTS:
		pathtodata - where is the original gdat.mat file
		DTdir - the data directory where the new data will be saved
	"""
	if not os.path.exists(DTdir):
		os.makedirs(DTdir) #create DT folder if it doesn't exist
		print 'made ' + DTdir
	if not os.path.exists(os.path.join(DTdir, 'gdat.hdf5')):
		print 'making ' + os.path.join(DTdir, 'gdat.hdf5')
		data = scipy.io.loadmat(pathtodata) #load raw data
		gdat = data['gdat']

		gdatfilepath = os.path.join(DTdir, 'gdat.hdf5')
		f = h5py.File(gdatfilepath)
		dset = f.create_dataset('gdat', data = gdat)
		f.close()
	else:
		print os.path.join(DTdir, 'gdat.hdf5') + ' already exists'

def load_datafile(subj, block, DTdir, elecs='', srate='',  Events=''):
	"""
	Loads instance of Subject data class if it has already been created, otherwise creates it with given parameters.
	elecs, srate, and Events need only be supplied if creating the instance, otherwise default to null because already exist in saved instance.
	"""
	pkl_filepath = os.path.join(DTdir, (subj + '_' + block + '.pkl'))
	if os.path.exists(pkl_filepath):
		pkl_file = open(pkl_filepath, 'rb')
		subject_instance = cPickle.load(pkl_file)
		pkl_file.close()
		print 'loading %s' %(pkl_filepath)
		return subject_instance
	else:
		print 'creating %s %s instance of Subject class' %(subj, block)
		return Subject(subj, block, elecs, srate, DTdir, Events)
