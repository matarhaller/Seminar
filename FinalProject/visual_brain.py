import mayavi.mlab as mlab
import numpy as np
import scipy.io 

data = scipy.io.loadmat('/Users/matar/Documents/MATLAB/Knight/electroderegistration/data_NC/NC_cortex.mat',struct_as_record = True)
brain = data['cortex']['vert'][0,0]
tri = data['cortex']['tri'][0,0]

elecs = scipy.io.loadmat('/Users/matar/Documents/Courses/PythonClass/FinalProject/elecs.mat')
elecs = elecs['els']

def plot_elecsonbrain(brain, tri, elecs):
	"""
	plots electrode spheres on brain
	INPUT:
		brain - xyz coordinates of cortex surface vertices (numpy array, 3 columns)
		tri - vertices in each triangle (numpy array, 3 columns)
		elecs - xyz coordinates of electrode locations (numpy array, 3 columns)
	"""
	mlab.triangular_mesh(brain[:,0],brain[:,1],brain[:,2],tri-1)
	mlab.points3d(elecs[:,0],elecs[:,1],elecs[:,2],scale_factor = 3)
