import SimpleXMLRPCServer
from scipy import ndimage
from scipy import misc
import pylab

class ImageManipulation:
	def rotate(self, imagefile, numdegrees):
		"""
		reads in png file, convert to nparray, rotate numdegrees
		"""
		img = misc.imread(imagefile)
		return ndimage.rotate(img, degrees)

	def crop(self,imagefile,amount):
		"""
		reads in png file, crops amount.
		amount is a tupe of (xamount yamount).
		xamount and yamount are < 1
		"""
		img = misc.imread(imagefile)
		shp = img.shape
		return img[shp[0]*amount[0]:-1*shp[0]*amount[0], shp[1]*amount[1]:-1*shp[1]*amount[1]]

	def gaussianfilter(self,imagefile,sigma):
		img = mis.imread(imagefile)
		return ndimage.gaussian_filter(img,sigma = sigma)

host, port = "", 5022
server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)
server.register_instance(Some_Class_We_Want_Remotely_Accessible())
server.register_multicall_functions() #enable multiple calls
server.register_introspection_functions() #to allow client to discover methods (can see docstrings of functions)
print "XMLRPC Server is starting at:", host, port