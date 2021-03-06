from enthought.traits.api import HasTraits, Range, Instance, on_trait_change
from enthought.traits.ui.api import View, Item, HGroup
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene

from numpy import linspace, pi, cos, sin

def curve(n_mer, n_long):
    phi = linspace(0, 2*pi, 2000)
    return [ cos(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
            sin(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
            0.5*sin(n_long*phi),
            sin(phi*n_mer)]

class Visualization(HasTraits):
	meridonal = Range(1, 30, 6)
	transverse = Range(0, 30, 11)
	scene = Instance(MlabSceneModel, ())

	def __init__(self):
		HasTraits.__init__(self)
		x, y, z, t = curve(self.meridonal, self.transverse)
		self.plot = self.scene.mlab.plot3d(x, y, x, t, colormap = 'Spectral')

	@on_trait_change('meridonal,transverse')
	def update_plot(self):
		x, y, z, t = curve(self.meridonal, self.transverse)
		self.plot.mlab_source.set(x=x, y=y, z=z, scalars = t)


	#layout of the dialog
	view = View(Item('scene', editor = SceneEditor(scene_class = MayaviScene), height = 250, width = 300, show_label = False),
		HGroup('_','meridonal','transverse',),)

visualization = Visualization()
visualization.configure_traits()