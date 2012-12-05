import os
import cPickle
import scipy.io
import numpy as np
import subj_globals
import h5py

#make Events creation compact, organize so that loading and making data are called correctly 

subj = 'ST26'
block = 'decision'
DTdir = os.path.join('/Users/matar/Documents/Courses/Python/data/', subj + '_' + block)
pathtodata = '/Users/matar/Documents/MATLAB/DATA/Stanford/ST26/data/decision/gdat.mat'

#make or load datafile (hdf5 file of gdat)
subj_globals.make_datafile(pathtodata,DTdir)

ANsrate = 2.4414e04
srate = 3.0518e03
bad_elecs = np.array([4,9,11,12,13,17,22,23,29,40,47,48,51,52,53,61,63,65, 66, 68, 69, 70, 71, 77, 91, 92, 95, 96]) #based on data
bad_elecs = bad_elecs-1 #make it 0 ordered
num_elecs = 96
elecs = np.setdiff1d(np.arange(num_elecs),bad_elecs)

#make Events dictionary from existing .mat files
EventsArray = scipy.io.load(os.path.join(DTdir, 'EventsArray.mat'))
stimonset = EventsArray['stimonset'].squeeze()
stimoffset = EventsArray['stimoffset'].squeeze()
responset = EventsArray['responset'].squeeze()
respoffset = EventsArray['respoffset'].squeeze()
badevent = EventsArray['badevent'].squeeze()
resp = EventsArray['resp'].squeeze()

sample = scipy.io.loadmat(os.path.join(DTdir, 'SAMPLE.mat'))
sample = sample['SAMPLE'].squeeze()

cresp = scipy.io.loadmat(os.path.join(DTdir, 'CORRECT.mat'))
cresp = cresp['CORRECT'].squeeze().tolist()
cresp = np.array([x[0] for x in cresp])

Events = dict()
Events['ANsrate'] = ANsrate
Events['stimonset'] = stimonset
Events['stimoffset'] = stimoffset
Events['responset'] = responset
Events['respoffset'] = respoffset
Events['resp'] = resp
Events['badevent'] = badevent
Events['sample'] = sample
Events['cresp'] = cresp

#Instantiate Subject class for this subject
ST26 = subj_globals.load_datafile(DTdir, subj, block, DTdir, elecs, srate,  Events)