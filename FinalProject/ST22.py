import os
import cPickle
import scipy.io
import numpy as np
import subj_globals
import tables as tb

SJdir = '/Users/matar/Documents/PyTest/'
subj = 'ST22'
block = 'decision'
data = scipy.io.loadmat('/Users/matar/Documents/MATLAB/DATA/Stanford/ST22/data/gdat.mat')
gdat = data['gdat']
ANsrate = 2.4414e04
srate = 3.0518e03
bad_elecs = np.array([4,9,11,12,13,17,22,23,29,40,47,48,51,52,53,61,63,65, 66, 68, 69, 70, 71, 77, 91, 92, 95, 96])
bad_elecs = bad_elecs-1 #make it 0 ordered
#Enum  = np.arange(96) #96 elecs
Enum = min(gdat.shape)
elecs = np.setdiff1d(Enum,bad_elecs)


num_elecs = min(gdat.shape) #number of keys (elecs)
array_dtype = gdat.dtype

class Record(tb.IsDescription):
	elec = tb.Int32Col()
	vrow = tb.Int32Col()

fid = tb.openFile('/Users/matar/Documents/Courses/Python/Seminar/FinalProject/ST26.h5','w')
atom = tb.Atom.from_dtype(gdat.dtype)
k = fid.createTable(fid.root, 'elecs', Record, expectedrows = num_elecs)
v = fid.createVLArray(fid.root, 'values', atom)

#feed data
row = k.row
for i in xrange(num_elecs):
	row['elec'] = i
	row['vrow'] = i
	row.append()
	value = gdat[i,:]
	v.append(value)
k.flush()
v.flush()
fid.close()

print 'result of fetches:'
print 'key = "2" --> ', v[k.readWhere('key == 2')['vrow'][0]]
print 'key = "0" --> ', v[k.readWhere('key == 0')['vrow'][0]]

fid = tb.openFile('/home/knight/matar/ST26.h5','r')


class gdatclass(tables.IsDescription):
	elec_number = tables.Int32Col()
	data = tables.Float64Col()

## make table for gdat
h5file = tables.openFile('/home/knight/matar/ST26.h5', mode = 'w', title = 'ST26 data file')

atom = tables.Atom.from_dtype(gdat.dtype)
ds = h5file.createCArray(h5file.root, 'ST26', atom, gdat.shape)
ds[:] = gdat
h5file.close()


group = h5file.createGroup("/", 'ST22', 'subject folder') #'/' is another way to refer to h5file.root. group is like directory
table = h5file.createTable(group, 'gdat', gdatclass, 'raw data')
electrode = table.row
for i in arange(Enum):
	electrode['elec_number'] = i
	electrode['data'] = gdat[i,:]
	electrode.append()
table.flush()



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
