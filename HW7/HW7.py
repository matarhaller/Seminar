from enthought.traits.api import HasTraits, Str, \
            Int, Float, Enum,DelegatesTo,This,Instance, Button
from enthought.traits.ui.api import View, Item, Group
import urllib2, json
from matplotlib.figure import Figure
from mpl_figure_editor import MPLFigureEditor
from skimage import io
import matplotlib.cm as cm
from skimage.filter import threshold_otsu
from skimage.transform import swirl
from scipy import ndimage
from skimage.feature import harris


def make_imgarray(inputstr):
	"""
	takes a string query, uses google api to search in images.google.com, parses result, and then returns the string corresponding to the 
	since some sites (wikipedia) don't allow to easily scrape their images, for now you'll just get a 'try again' for a different search item
	"""
	inputstr = inputstr.split()
	parsedlist = [urllib2.quote(s.encode("utf8")) for s in inputstr]
	parsedlist = [s+'+' for s in parsedlist]
	finalinput = ''.join(parsedlist)
	key = 'AIzaSyDxNRMd-FUH3jhiJo5Cf5dBMiaUgJuBDno'
	cx = '017499574283461742247:k3isvnhbqog'
	url = 'https://www.googleapis.com/customsearch/v1?key=' + key + '&cx=' + cx + '&q='+ finalinput
	result = json.load(urllib2.urlopen(url))
	try:
		imghtml = result['items'][0]['pagemap']['cse_image'][0]['src']
	except:
		imghtml = 'http://www.adnoiseam.net/store/images/belladonnakillz-sorry_try_again.jpg'
	imgstr = urllib2.urlopen(imghtml).read()
	fig = open('image.jpg','w').write(imgstr)
	imgarray = io.imread('image.jpg')
	return url, imgarray

		
class ImgManip(HasTraits):
	query = Str('Type a query')
	url = Str
	refresh = Button()
	figure = Instance(Figure,())
	imgarray = ""
	prev_array = ""
	thresh = Button()
	swirled = Button()
	rotate = Button()
	undo = Button()

	def _query_changed(self,old, new):
		self.query = new

	def _refresh_fired(self):
		newurl, imgarray = make_imgarray(self.query)
		self.imgarray = imgarray
		self.url = newurl
		self.showimage()

	def _thresh_fired(self):
		self.prev_array= self.imgarray
		self.do_threshold()
		self.showimage()

	def _swirled_fired(self):
		self.prev_array= self.imgarray
		self.do_swirl()
		self.showimage()

	def _rotate_fired(self):
		self.prev_array = self.imgarray
		self.do_rotate()
		self.showimage()

	def _undo_fired(self):
		self.do_undo()
		self.showimage()

	def showimage(self):
		ax = self.figure.add_subplot(111)
		ax.imshow(self.imgarray, cmap = cm.gist_gray)
		self.figure.canvas.draw()

	def do_threshold(self):
		"""
		threshold image
		"""
		thrsh = threshold_otsu(self.imgarray)
		self.imgarray = self.imgarray>thrsh

	def do_swirl(self):
		"""
		swirl image
		"""
		swirled = swirl(self.imgarray, rotation=0, strength=10, radius=150, order=2)
		self.imgarray = swirled

	def do_rotate(self):
		""" if you rotate after thresholding, then the image looks weird"""
		rotated = ndimage.rotate(self.imgarray, 90)
		self.imgarray=rotated

	def do_undo(self):
		""" 1 step undo """
		self.imgarray = self.prev_array

## configure gui appearance
view1 = View(Item('query',width = -250,resizable=True,label = "Query String",full_size=True), Item('refresh',resizable = True, label = "Refresh Image"), Item('url',width = -250, resizable = True, padding = 2, label = "Image URL",full_size=True), Item('figure', show_label = False, width = 600, height = 600, resizable = True, editor = MPLFigureEditor()), Item('thresh', label = 'Threshold',show_label=False), Item('swirled',resizable=False,label = 'Swirl',show_label=False), Item('rotate',resizable=False,label="Rotate 90",show_label=False),Item('undo',resizable=False,label="UNDO",show_label=False))

i = ImgManip(); i.configure_traits(view = view1)