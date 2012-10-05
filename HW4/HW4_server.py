import SimpleXMLRPCServer

class ImageManipulation:
	from scipy import ndimage
	from scipy import misc
	import numpy as np
	def rotate(self, img, numdegrees):
		"""
		receives image file as list. converts to nparray, saves as _pre rotate numdegrees, save as _post. transmits back list.
		"""
		img = np.array(img) #convert to array from list
		scipy.misc.imsave('img_rotate_pre.png',img) #save original
		img_rotate = ndimage.rotate(img, degrees)
		scipy.misc.imsave('img_rotate_post.png',img_rotate) #save rotated
		return img_rotate.tolist() #return as list
 
	def crop(self,img,amount):
		"""
		receives image file as list, converts to nparray, saves as _pre. crops amount. saves as _post, transmits back list.
		amount is a tupe of (xamount yamount).
		xamount and yamount are < 1 (ex:0.25)
		"""
		img = np.array(img)
		scipy.misc.imsave('img_crop_pre.png',img)
		shp = img.shape
		img_crop = img[shp[0]*amount[0]:-1*shp[0]*amount[0], shp[1]*amount[1]:-1*shp[1]*amount[1]]
		scipy.misc.imsave('img_crop_post.png',img_crop)
		return img_crop.tolist()

	def gaussianfilter(self,img,sigma):
		"""
		receives images file as list, converts to nparray, saves as _pre. applies gaussian filter, saves as _post. transmits back list.
		"""
		img = np.array(img) #convert to array from list
		scipy.misc.imsave('img_blurr_pre.png',img)
		img_blurr = ndimage.gaussian_filter(img,sigma = sigma)
		scipy.misc.imsave('img_blurr_post.png',img_blurr)
		return img_blurr.tolist()

host, port = "", 5024
server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)
server.register_instance(ImageManipulation())
server.register_multicall_functions() #enable multiple calls
server.register_introspection_functions() #to allow client to discover methods (can see docstrings of functions)
print "XMLRPC Server is starting at:", host, port

server.serve_forever()