"""
Write an XML-RPC server/client program pair.
• The server offers 3 methods providing lossless image manipulation (be creative). Each server method must have descriptive documentation accessible by the client.
• The client calls each method on the server machine with an array from an image.
• Client saves the original image and modified image received from the server. Server saves image received from the client and modified image.
• Include example images in your solutions, and test by running this through your local loopback ip address. If you’d like to test from a remote computer, come to OH and we will be set up to test your program over the network.
• localhost ip = 127.0.0.1

 Be creative with the server methods, but make sure the operations can be explained simply in English. An example might be to switch color channels and reverse the order of the values in one channel. Make sure to think about properly dealing with differently shaped image arrays (methods should be compatible with both 3-color and grayscale). Lastly, XMLRPC won’t transmit arrays, so you’ll have to convert to another data structure.
"""


import xmlrpclib, sys
import matplotlib.pyplot as plt
import pylab
from scipy import ndimage
from scipy import misc
import numpy as np

print '-'*50
print "question 1 - server client image manipulation"
print "need to run HW4_server.py"

img = misc.imread('../HW2/data/e37.png')
scipy.misc.imsave('img_orig.png',img)
img = img.tolist() #convert to list for transmission

host, port = "", 5024
server = xmlrpclib.ServerProxy("http://%s:%d" % (host, port))
available_methods = server.system.listMethods() #list of available methods
print "methods from server:"
for method in available_methods:
    print "\n" + method

print "making & saving rotated image \n"
img_rotate = server.rotate(img, 45) #transmit list, rotate 45 degrees
img_rotate= np.array(img_rotate) #receive list, so convert to array
scipy.misc.imsave('img_rotate.png',img_rotate) #save array as png
print "making & saving cropped image \n"
img_crop = server.crop(img, (0.25,0.25))
img_crop = np.array(img_crop)
scipy.misc.imsave('img_crop.png',img_crop)
print "making & saving blurred image"
img_blurr = server.gaussianfilter(img, 2)
img_blurr = np.array(img_blurr)
scipy.misc.imsave('img_blurr.png',img_blurr)
