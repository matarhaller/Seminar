import os
import cPickle
import scipy.io
import numpy as np
import subj_globals


SJdir = '/Users/matar/Documents/PyTest/'
subj = 'ST22'
block = 'decision'
data = scipy.io.loadmat('/Users/matar/Documents/MATLAB/Knight/DATA/ST22/data/gdat.mat')
gdat = data['gdat']
ANsrate = 2.4414e04
srate = 3.0518e03
bad_elecs = np.array([4,9,11,12,13,17,22,23,29,40,47,48,51,52,53,61,63,65, 66, 68, 69, 70, 71, 77, 91, 92, 95, 96])
bad_elecs = bad_elecs-1 #make it 0 ordered
Enum  = np.arange(96) #96 elecs
elecs = np.setdiff1d(Enum,bad_elecs)


stimonset = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/stimonset.mat')
stimonset = stimonset['stimonset'].squeeze()

stimoffset = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/stimoffset.mat')
stimoffset = stimoffset['stimoffset'].squeeze()

responset = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/responset.mat')
responset = responset['responset'].squeeze()

respoffset = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/respoffset.mat')
respoffset = respoffset['respoffset'].squeeze()

badevent = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/badevent.mat')
badevent = badevent['badevent'].squeeze()

resp = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/resp.mat')
resp = resp['resp'].squeeze()

sample = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/SAMPLE.mat')
sample = sample['SAMPLE'].squeeze()

cresp = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/CORRECT.mat')
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

ST22 = subj_globals.Subject(subj, block, elecs, srate, gdat, SJdir, Events)



#save_dataobj(ST22)
#ST22 = cPickle.load(open("/Users/matar/Documents/PyTest/ST01/data/test/alldata.pic", 'r'))
