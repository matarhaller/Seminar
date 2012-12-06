#cython: cdivision = True
import cython
cimport numpy as np
import numpy as np
import math
import h5py

@cython.boundscheck(False)
@cython.wraparound(False) #cancel ability to do -1 for last element
def CARcython(np.ndarray elecs, np.ndarray chRank, np.ndarray groups, int Ngroups, int numelecs, char gdatfilename):
	
	f = h5py.File(gdatfilename,'a')
	gdat = f['gdat']

	cdef int e, cnt
	cdef np.ndarray gdat_CAR = gdat
	cdef np.ndarray CAR = np.zeros(Ngroups, max(gdat.shape))
	cdef np.ndarray CAR_all = np.zeros(max(gdat.shape))

	for e in elecs:
		gdat_CAR[e,:] = gdat[e,:] - np.mean(gdat[e,:])
		if chRank[e]:
			CAR[groups[e],:] = CAR[groups[e],:] + gdat_CAR[e,:]

	for cnt in np.prange(Ngroups):
		if np.sum(chRank[np.flatnonzero(groups == cnt)]):
			CAR[cnt,:] = np.divide(CAR[cnt,:], np.sum(chRank[np.flatnonzero(groups == cnt)]))

	for e in np.prange(numelecs):
		gdat_CAR[e,:] = gdat_CAR[e,:] - CAR[groups[e],:]
		if chRank[e]:
			CAR_all = CAR_all + gdat_CAR[e,:]

	CAR_all = np.divide(CAR_all, len(elecs))

	return CAR_all, gdat_CAR, CAR

# pull three loops out into sep functions - only they will be in cython and compiled. write them in a separate file completely - in setup.py run them and compile them separately. can just feed it in the file object to the gdat or the filepath. in cython code can open the db and do for item in db. from comiled cython code import blah, on this file object/path do whatever.
# write cython code (code.pyx) where do cdef to define function, run cython on it one time (definied in setup.py) - makes code.co file - then in here (python file) from code import function. now function is a python function (reads it in from code.so) or look at numexpr.