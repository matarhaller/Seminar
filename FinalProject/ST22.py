import os
import cPickle
import scipy.io
import numpy as np
import subj_globals
import h5py

subj = 'ST22'
block = 'decision'
DTdir = os.path.join('/Users/matar/Documents/Courses/Python/data/', subj + '_' + block)


"""
#make data file - only need to run once
data = scipy.io.loadmat('/Users/matar/Documents/MATLAB/DATA/Stanford/ST22/data/gdat.mat')
gdat = data['gdat']

gdatfilepath = os.path.join(DTdir, 'gdat.hdf5')
f = h5py.File(gdatfilepath)
dset = f.create_dataset('gdat', data = gdat)
f.close()
"""

ANsrate = 2.4414e04
srate = 3.0518e03
bad_elecs = np.array([4,9,11,12,13,17,22,23,29,40,47,48,51,52,53,61,63,65, 66, 68, 69, 70, 71, 77, 91, 92, 95, 96]) #based on data
bad_elecs = bad_elecs-1 #make it 0 ordered
num_elecs = 96
elecs = np.setdiff1d(np.arange(num_elecs),bad_elecs)

stimonset = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/stimonset.mat')
stimonset = stimonset['stimonset'].squeeze()

stimoffset = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/stimoffset.mat')
stimoffset = stimoffset['stimoffset'].squeeze()

responset = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/responset.mat')
responset = responset['responset'].squeeze()

respoffset = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/respoffset.mat')
respoffset = respoffset['respoffset'].squeeze()

badevent = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/badevent.mat')
badevent = badevent['badevent'].squeeze()

resp = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/resp.mat')
resp = resp['resp'].squeeze()

sample = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/SAMPLE.mat')
sample = sample['SAMPLE'].squeeze()

cresp = scipy.io.loadmat('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/CORRECT.mat')
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

ST22 = subj_globals.Subject(subj, block, elecs, srate, DTdir, Events)


#save_dataobj(ST22)
#ST22 = cPickle.load(open("/Users/matar/Documents/PyTest/ST01/data/test/alldata.pic", 'r'))
