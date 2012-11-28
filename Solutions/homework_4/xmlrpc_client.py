#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 3 Solutions
Author: Christopher Klein, modified by Isaac Shivvers

IMPORTANT NOTE ABOUT IMAGE ARRAYS, NUMPY ARRAYS, AND LISTS:
Images on computers are generally stored as unsigned 8-bit integers, but
that data type is not conserved when we convert a numpy array to a list
and then back.  So, when reforming an array from a list of values,
(the format in which we must send images throug XMLRPC), we must 
explicitly cast them with dtype uint8, else the colors get wonky.

"""
import xmlrpclib
from numpy import array, append, shape
from matplotlib import pyplot

# Connect to the server.
host, port = "", 5020
server = xmlrpclib.ServerProxy("http://%s:%d" % (host, port))

# Get a list of methods available on the server and print them out, along with 
# their docstrings.
available_methods = server.system.listMethods()
print "Available methods from server:\n"+'*'*50+'\n'
for method in server.system.listMethods():
    print method
    print ' - '+server.system.methodHelp(method) + '\n'
print '*'*50+'\n'
# Read in an image and save it as the original for later comparison.
im_array = pyplot.imread("cake.jpg")
pyplot.imshow(im_array)
pyplot.savefig("client_original.png")
# Convert the original image array to a list, because we cannot send an array
# over the XMLRPC connection.
im_list = im_array.tolist()

# Call the image distortion method on the original image list.
print 'calling image_distort_1...'
distorted_im_list = server.image_distort_1(im_list)
# Create an array from the returned distorted image list.
#  See note in header for explanation of dtype flag.
distorted_im_array = array(distorted_im_list, dtype='uint8')

# Write out the distorted image.
pyplot.imshow(distorted_im_array)
pyplot.savefig("client_distorted1.png")


# Same as above, but for the second distortion method.
print 'calling image_distort_2...'
distorted_im_list = server.image_distort_2(im_list)
distorted_im_array = array(distorted_im_list, dtype='uint8')
pyplot.imshow(distorted_im_array)
pyplot.savefig("client_distorted2.png")

# Same as above, but for the third distortion method.
print 'calling image_distort_3...'
distorted_im_list = server.image_distort_3(im_list)
distorted_im_array = array(distorted_im_list, dtype='uint8')
pyplot.imshow(distorted_im_array)
pyplot.savefig("client_distorted3.png")

