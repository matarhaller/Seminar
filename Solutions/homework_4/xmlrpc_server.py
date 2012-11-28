#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 3 Solutions
Author: Christopher Klein
Modified: Isaac Shivvers

IMPORTANT NOTE ABOUT IMAGE ARRAYS, NUMPY ARRAYS, AND LISTS:
Images on computers are generally stored as unsigned 8-bit integers, but
that data type is not conserved when we convert a numpy array to a list
and then back.  So, when reforming an array from a list of values,
(the format in which we must send images throug XMLRPC), we must 
explicitly cast them with dtype uint8, else the colors get wonky.

"""
import SimpleXMLRPCServer, sys
from numpy import array, append, shape
from matplotlib import pyplot 

#########################################################
# define all of the functions we want available
def image_distort_1(im_list):
    """
    Multiply each pixel value by 0.5
    """
    # Convert the list back to an array for easier manipulation.
    im_array = array(im_list)
    # save the figure for reference
    #  See discussion in header for explanation of dtype flag
    pyplot.imshow(im_array.astype("uint8"))
    pyplot.savefig("server_received1.png")
    # Perform the distortion operation.
    distorted_im_array = im_array*0.5
    # Write out the distorted image.
    pyplot.imshow(distorted_im_array.astype("uint8"))
    pyplot.savefig("server_distorted1.png")
    # Convert the distorted image array back to a list to transport to 
    # client.
    distorted_im_list = distorted_im_array.tolist()
    return distorted_im_list

def image_distort_2(im_list):
    """
    Move bottom third of rows to the top
    """
    im_array = array(im_list)
    pyplot.imshow(im_array.astype("uint8"))
    pyplot.savefig("server_received2.png")
    distorted_im_array = append(im_array[shape(im_array)[0]/3:], 
        im_array[:shape(im_array)[0]/3], 0)
    pyplot.imshow(distorted_im_array.astype("uint8"))
    pyplot.savefig("server_distorted2.png")
    distorted_im_list = distorted_im_array.tolist()
    return distorted_im_list

def image_distort_3(im_list):
    """
    Subsample the image by 2 and then repeat it out in a 2x2 new image 
    called the "add_image". Then add this to the original image.
    """
    im_array = array(im_list)
    pyplot.imshow(im_array.astype("uint8"))
    pyplot.savefig("server_received3.png")
    sub_im = im_array[::2, ::2]
    sub_im2 = append(sub_im, sub_im, 0)
    add_array = append(sub_im2, sub_im2, 1)
    distorted_im_array = im_array + add_array
    pyplot.imshow(distorted_im_array.astype("uint8"))
    pyplot.savefig("server_distorted3.png")
    distorted_im_list = distorted_im_array.tolist()
    return distorted_im_list


host = ""
# Allow the user to change the port number when running the script. If no port
# number is provided, use a default.
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 5020


# Here we set up the server.
server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port), allow_none=True)

# Register the all of the functions that we want to serve.
server.register_function(image_distort_1)
server.register_function(image_distort_2)
server.register_function(image_distort_3)
# Also, register introspection functions to allow the client to list the 
# available methods and their docstrings.
server.register_introspection_functions()

# Start serving, and continue to do so until killed with control-c.
print "XMLRPC Server is starting at:", host, port
server.serve_forever()