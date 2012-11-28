import os
import cPickle
import scipy.io
import numpy as np

from create_subj_globals import subj_globals

def save_dataobj(dataobj): #gives memory error with pickle and cPickle - should reduce size?
	""" save the object to file to be read later"""
	filename = os.path.join(dataobj.DTdir, 'alldata.pic')
	with open (filename, 'wb') as output:
		cPickle.dump(dataobj, output, cPickle.HIGHEST_PROTOCOL)

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

ST22 = subj_globals(subj, block, elecs, ANsrate, srate, gdat, SJdir)
save_dataobj(ST22)
ST22 = cPickle.load(open("/Users/matar/Documents/PyTest/ST01/data/test/alldata.pic", 'r'))
