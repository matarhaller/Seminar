import mayavi.mlab as mlab
import numpy as np
import scipy.io
import os
import subj_globals

subj = 'ST26'
block = 'decision'
DTdir = os.path.join('/Users/matar/Documents/Courses/Python/data/', subj + '_' + block)

dataobj = subj_globals.load_datafile(subj, block, DTdir)


# load data
data = scipy.io.loadmat(os.path.join(dataobj.DTdir, 'cortex.mat'), struct_as_record = True)
elecmatrix = scipy.io.loadmat(os.path.join(dataobj.DTdir, 'elecmatrix.mat'))

# xyz coordinates of cortex surface vertices (numpy array, 3 columns)
brain = data['cortex']['vert'][0,0]

# vertices in each triangle (numpy array, 3 columns)
tri = data['cortex']['tri'][0,0]

# xyz coordinates of electrode locations (numpy array, 3 columns)
elecs = elecmatrix['elecmatrix']

# disable rendering (brings up figure faster)
figure = mlab.gcf()
mlab.clf()
figure.scene.disable_render = True

# plot brain and electrodes
cortex = mlab.triangular_mesh(brain[:,0],brain[:,1],brain[:,2],tri-1, colormap = 'gray')
electrodes = mlab.points3d(elecs[:,0],elecs[:,1],elecs[:,2],scale_factor = 3, color = (1, 0 , 0), resolution = 20)

selectedpoint = mlab.points3d(elecs[0,0],elecs[0,1],elecs[0,2], scale_factor = 3, color = (0,1,0), resolution = 20) #first electrode is green

# reenable rendering (all objects have been created)
figure.scene.disable_render = False

# grab points describing individual electrode
elec_points = electrodes.glyph.glyph_source.glyph_source.output.points.to_array()

def picker_callback(picker):
	""" picker callback - gets called when pick events
	"""
	if picker.actor in electrodes.actor.actors:
		# find which data point corresponds to the point picked:
		# we have to account for the fact that each data point is represented by an electrode/glyph with several points
		point_id = picker.point_id/elec_points.shape[0]
		# if a null spot has been selected, we have '-1'
		if point_id !=-1:
			print 'electrode ' + str(point_id) #0 start numbering (matlab - 1)
			# retreive the coordinates corresponding to that data point
			x, y, z = elecs[:,0][point_id], elecs[:,1][point_id], elecs[:,2][point_id]

			# make selected electrode green
			selectedpoint.mlab_source.set(x =x, y = y, z = z)

			dataobj.plot_trace(point_id)


picker = figure.on_mouse_pick(picker_callback)
# decrease the tolerance so that can easily select precise point
picker.tolerance = 0.01

mlab.title('select an electrode')

mlab.show()