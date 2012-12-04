import os
import cPickle
import scipy.io
import numpy as np
import subj_globals
import h5py

#make Events creation compact, organize so that loading and making data are called correctly 

subj = 'ST22'
block = 'decision'
DTdir = os.path.join('/Users/matar/Documents/Courses/Python/data/', subj + '_' + block)
pathtodata = '/Users/matar/Documents/MATLAB/DATA/Stanford/ST22/data/gdat.mat'

def make_datafile(pathtodata, DTdir):
	"""
	make hdf5 data file - will only run once
	INPUTS:
		pathtodata - where is the original gdat.mat file
		DTdir - where will the new data be saved
	"""
	if not os.path.exists(os.path.join(DTdir, 'gdat.hdf5')):
		data = scipy.io.loadmat(pathtodata)
		gdat = data['gdat']

		gdatfilepath = os.path.join(DTdir, 'gdat.hdf5')
		f = h5py.File(gdatfilepath)
		dset = f.create_dataset('gdat', data = gdat)
		f.close()
	else:
		print os.path.join(DTdir, 'gdat.hdf5') + ' already exists'

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

def load_data(DTdir, subj, block, DTdir, elecs='', srate='',  Events=''):
	"""
	Loads instance of Subject data class if it has already been created, otherwise creates it with given parameters.
	elecs, srate, and Events need only be supplied if creating the instance, otherwise default to null because already exist in saved instance.
	"""
	pkl_filepath = os.path.join(DTdir, (subj + '_' + block + '.pkl'))
	if os.path.exists(pkl_filepath):
		pkl_file = open(pkl_filepath, 'rb')
		ST22 = cPickle.load(pkl_file)
		pkl_file.close()
		print 'loading %s' %(pkl_filepath)
	else:
		ST22 = subj_globals.Subject(subj, block, elecs, srate, DTdir, Events)
		print 'creating %s %s instance of Subject class' %(subj, block)

#save_dataobj(ST22)
#ST22 = cPickle.load(open("/Users/matar/Documents/PyTest/ST01/data/test/alldata.pic", 'r'))
