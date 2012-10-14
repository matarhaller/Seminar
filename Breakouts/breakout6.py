"""
Image registration

Consider two satellite views of the same area:
webreg_0.jpg webreg_1.jpg
Load and display the images.
Estimate the affine transform that would fit these images together.
Apply the transform and combine the two images.
Hints:
Look at skimage.transform.
Use matplotlib's ginput to find point coordinates.
The process of aligning and combining images is known as "image registration".
"""
import matplotlib.pyplot as plt
import numpy as np
from pylab import ginput
from skimage.transform import PiecewiseAffineTransform


img0 = np.flipud(plt.imread('/Users/matar/Documents/Courses/python-seminar/Lectures/05_scikit-image/scikit-image/breakout/register/webreg_0.jpg'))


img1 = np.flipud(plt.imread('/Users/matar/Documents/Courses/python-seminar/Lectures/05_scikit-image/scikit-image/breakout/register/webreg_1.jpg'))


fig = plt.figure()
ax = fig.add_subplot(1,2,1)
ax.imshow(img0, interpolation = 'nearest')
ax.set_title('image 0')
ax2 = fig.add_subplot(1,2,2)
ax2.imshow(img1, interpolation = 'nearest')
ax2.set_title('image 1')

print "click 3 times on image 0\n"
pts0 = ginput(3) #points are returned as tuples
print "click 3 times on image 1\n"
pts1 = ginput(3)

tform = PiecewiseAffineTransform()
tform.estimate(pts0,pts1)