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
import scipy.signal
import matplotlib.pyplot as plt


def create_CAR(dataobj, grouping): 
	# trying to implement in cython because slow. see CARcython.pyx
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
	gdat_CAR = subgroup.create_dataset('gdat', data = gdat) 
	#keep gdat name within CAR subgroup so that can be easily accessed later.
	CAR = subgroup.create_dataset('CAR', shape = (Ngroups, max(gdat.shape)), dtype = gdat.dtype)
	CAR_all = subgroup.create_dataset('CAR_all', shape = (1, max(gdat.shape)), dtype = gdat.dtype)
	gdat_CAR_group = subgroup.create_dataset('CAR_group', shape = gdat.shape, dtype = gdat.dtype)

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


def analytic_amp(dataobj, elec, f1=70, f2=150):
	"""
	filters signal using a flat gaussian then does the hilbert transform.
	returns analytic amplitude.
	runs on 1 electrode
	slow because of fft and ifft - need to fix (use fftw)
	INPUT:
		elec = electrode number
		f1, f2 = upper and lower bounds to filter
				defaults to 70Hz, 150Hz (broadband high gamma)
	signal is in the time domain
	will run only after CAR has been calculated
	"""
	#load in gdat data
	f = h5py.File(dataobj.gdat,'a')
	try:
		gdat = f['CAR']['gdat_CAR']
	except:
		print "won't do hilbert until calculate CAR"
		return

	band = gdat_CAR[elec,:] #1 electrode's data

	subgroup = f.create_group("hilbert")
	name = 'e'+str(elec)
	aa = subgroup.create_dataset(name, shape = band.shape, dtype = band.dtype)

	max_freq = dataobj.srate / 2
	df = 2 * max_freq / max(band.shape)
	center_freq = (f1 + f2) / 2
	filter_width = f2 - f1

	x = np.arange(0, max_freq, df)

	gauss = np.exp( - (x - center_freq)**2)
	cnt_gauss = round(center_freq / df)
	flat_padd = round(filter_width / df)
	padd_left = math.floor(flat_padd / 2)
	padd_right = math.ceil(flat_padd / 2)
	our_wind = np.hstack((gauss[(padd_left+1):cnt_gauss], np.ones(flat_padd), gauss[(cnt_gauss+1):(-1-padd_right)]))

	our_wind = np.hstack((our_wind, np.zeros(max(gdat.shape)-len(our_wind))))

	y = scipy.fftpack._fftpack.zfft(band) #slow, check fftw options. gives diff answer from matlab.

	our_wind[1] = our_wind[1] / 2 
	#our_wind = np.tile(our_wind, (0, 1))*2 #should be (size(input, 1),1)
	our_wind = our_wind*2

	aa = np.fft.ifft(np.multiply(y,our_wind)) #TOO SLOW

	#close file
	f.close()

	#log the change
	dataobj.logit('hilbert transform - elec %i\n\t%iHz - %iHz\nadded to %s' %(elec, f1, f2, dataobj.gdat))

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

		#methods defined outside (so can eventually optimize)
		self.create_CAR = create_CAR #common ave ref method (defined above)
		self.analytic_amp = analytic_amp #aa method (defined above)

		self.gdat = os.path.join(DTdir, 'gdat.hdf5') #filepath to hdf5 file containing raw data

	def logit(self, message):
		"""
		keep a log of all analyses done
		"""
		logf = open(self.logfile, "a")
		logf.write('\n[%s] %s\n' % (datetime.datetime.now(), message))
		logf.flush()
		logf.close()

	def resampleEvents(self): 
		"""
		Resamples Events ANsrate to match data srate
		Updates Events ANsrate.
		"""
		## need to implement resampling for data itself too - upfirdn requires making filter.
		labels = {'stimonset','stimoffset','responset','respoffset'}
		for k in self.Events.keys():
			if k in labels:
				self.Events[k] = np.round(self.Events[k] / self.Events['ANsrate'] * self.srate)
		self.logit('resampled Events from %f to %f' %(self.Events['ANsrate'], self.srate))
		
		#update ANsrate
		self.Events['ANsrate'] = self.srate
		self.logit("updated Events['ANsrate'] to %f" %(self.srate))

	def calc_acc(self):
		"""
		calculate subject accuracy per trial, store in Events, print mean acc
		drops ambiguous stimuli from calculation. Events['acc'] will be shorter than other Events values because only calculates for nonambiguous stimuli
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

	def makeTrialsMTX(self,elec,raw = 'CAR', Params=dict()):
		#baseline corrects and makes a trialsmtx (not by conditions)
		#takes hilbert or something.
		#does it for an electrode, then stores it. before recalculates, checks that hasn't already been calculated
		#currently drops ambiguous stimuli - need to decide if to keep and how
		#makes a new file TrialsMTX.hdf5 with the dataMTX for each elec
		#need to implement by conditions
		"""
		INPUT:
			elec - electrode number
			raw - if to calculate from raw trace ('CAR') or 'from hilbert' 
				(optional, default 'CAR')
			Params - dictionary of onset/offset times for trial and for baseline (optional)
		"""

		# load data file
		f = h5py.File(self.gdat,'a')
		try:
			gdat = f[raw]['gdat_CAR'] #need to rerun CAR so gdat_CAR can be gdat
			band = gdat[elec,:]
		except:
			print 'either ' + raw + " not supported as 'raw' argument or elec out of bounds"
			return

		#default Params:
		if not Params: #empty dict
			Params['st'] = 0		#start time point (ms)
			Params['en'] = 3000		#end time point (ms)
			Params['bl_st'] = -250	#baseline start (ms)
			Params['bl_en'] = -50	#basline end (ms)

		# convert Params and Events to sampling rate
		for k in Params.keys():
			Params[k] = round(Params[k] / 1000 * self.srate)

		self.resampleEvents()

		# find correct trials
		if not 'acc' in self.Events.keys():
			self.calc_acc()

		correct = self.Events['acc'] == 1
		trials = np.flatnonzero(correct)

		#get size/shape arguments
		Ntrials = len(trials)
		triallength = Params['en'] - Params['st']

		# create data:
		# if dataMTX already exists,  load it. if not, then calculate.
		filename = os.path.join(self.DTdir, 'TrialsMTX.hdf5')
		f = h5py.File(filename, 'a')
		name = 'e'+str(elec)

		try:
			f[raw] # see if any electrode with that preprocessing has been run
			try: # see if this particular electrode has been run before
				dataMTX = f[raw][name]
				print 'loading electrode: ' + name
				return dataMTX
			except: #preprocess has been done, elec hasn't
				print 'creating electrode: ' + name
				dataMTX = f[raw].create_dataset(name, shape = (Ntrials, triallength), dtype = band.dtype)
		except: # all new
			print 'creating group: ' + raw + ' and electrode: ' + name
			subgroup = f.create_group(raw)
			dataMTX = subgroup.create_dataset(name, shape = (Ntrials, triallength), dtype = band.dtype)
		
		#cond = Events['sample'][trials]
		#conditions = np.unique(cond)

		#define onset times per trial
		st_tm = self.Events['stimonset'][trials]+Params['st']
		en_tm = self.Events['stimonset'][trials]+Params['en']

		#define baseline per trial
		bl_st_tm = self.Events['stimonset'][trials]+Params['bl_st']
		bl_en_tm = self.Events['stimonset'][trials]+Params['bl_en']
		
		#make data matrix
		for i, x in enumerate(st_tm):
			window = np.arange(st_tm[i], en_tm[i]).astype(int)
			blwindow = np.arange(bl_st_tm[i], bl_en_tm[i]).astype(int)
			dataMTX[i,:] = band[window] - np.mean(band[blwindow])

		self.logit('created dataMTX for electrode %i' %(elec))
		return dataMTX

	def plot_trace(self, elec, raw = 'CAR', Params = dict()):
		"""
		plots trace for the trial duration using TrialsMTX
		INPUT:
			elec - electrode number
			raw - if to calculate from raw trace ('CAR') or 'from hilbert' 
				(optional, default 'CAR')
			Params - dictionary of onset/offset times for trial and for baseline (optional)
		"""
		dataMTX = self.TrialsMTX(elec, raw, Params)

		plot_tp = 200 / 1000 * self.srate
		cut = 500 / 1000 * self.srate

		# convert Params to srate
		for k in Params.keys():
			Params[k] = round(Params[k] / 1000 * self.srate)

		x = np.array(range(Params['st'], Params['en']+1))
		f, ax = plt.subplots(1,1)
		ax.axhline(y = 0,color = 'k',linewidth=2)
		ax.axvline(x = 0,color='k',linewidth=2)
		ax.axvline(x = cue,color = 'gray',linewidth = 2)
		ax.axvline(x = cue+cue,color = 'gray',linewidth = 2)
		ax.axvspan(cue, cue+cue, facecolor='0.5', alpha=0.25,label = 'cue')

		ax.plot(x, dataMTX, linewidth = 2, color = 'blue')

		ax.set_xlim(Params['st'], Params['en'])
		ax.xaxis.set_ticklabels(['', '0', '','500', '', '1000', '', '1500', '', '2000','','2500','', '3000'],minor=False)
		ax.xaxis.set_ticks(range(Params['st'],Params['en'],plot_tp))
		ax.xaxis.set_tick_params(labelsize = 14)
		ax.yaxis.set_tick_params(labelsize=14)
		xticklabels = plt.getp(plt.gca(), 'xticklabels')
		yticklabels = plt.getp(plt.gca(), 'yticklabels')
		plt.setp(xticklabels, fontsize=14, weight='bold')
		plt.setp(yticklabels, fontsize=14, weight='bold')

		for pos in ['top','bottom','right','left']:
			ax.spines[pos].set_edgecolor('gray')
			ax.get_xaxis().tick_bottom()
			ax.get_yaxis().tick_left()

		plt.show()


#startup functions
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
	Loads instance of Subject data class if it has already been created, otherwise creates it with given parameters and saves in DTdir.
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
		subject = Subject(subj, block, elecs, srate, DTdir, Events)
		subject.save_dataobj() #saves it in DTdir
		return subject
