'''
Brushing code, PySci homework 2, Fall 2012

Isaac Shivvers, ishivvers@berkeley
'''

import numpy as np
import matplotlib.pyplot as plt
from brusher import Brusher

def plot_array(data, names):
    '''Create an array of plots.

    Expects data to be a tuple of 2d arrays, one entry for each subplot
    where array[0] --> x_coords and array[1] --> y_coords
    
    Expects names to be a 1d list of names to put in central axes.

    Returns a figure object and the associate array of axes.
    '''

    size = int(len(data)**.5)
    f, ax = plt.subplots(nrows=size, ncols=size) # build an array of subplot axes
    plt.subplots_adjust(hspace=0.1)   # reset the distances between subplots
    plt.subplots_adjust(wspace=0.1)
    
    # need to assign each point a color individually, for the brusher to work
    #  see brusher.py for more info on this
    # each rgba entry in colors is four numbers between 0 and 1,
    #  representing [red, green, blue, transparency]
    colors = np.zeros( (len(data[0][0]),4) )
    colors[:,2] = 1.0 # this is blue (i.e. rbg = [0, 0, 1])
    colors[:,3] = 0.75 # set the transparency (alpha) to .75, because it looks pretty that way
    
    count = 0
    for row in range(size):  # loop over features
        for col in range(size):
            axxx = ax[row,col]            
            p = axxx.scatter(data[count][0], data[count][1], c=colors)
            plt.setp(axxx.get_xticklabels(), visible=False)  # don't show ticks,
            plt.setp(axxx.get_yticklabels(), visible=False)  #  they clutter the plot
            if row==col: #put in a text label
                axxx.annotate(names[row], (10,-15), xycoords='axes points')
            count +=1 
    return f



######################## main code ########################

# read in iris data and format it properly for the brusher
dt = np.dtype({'names':['sep_len','sep_wid','pet_len','pet_wid','class'], 'formats':[float, float, float, float, 'S15']})
data = np.loadtxt('iris.data', dtype=dt, delimiter=',')
names = ['sep_len','sep_wid','pet_len','pet_wid']
dd = []
for i, nrow in enumerate(names):
    for j, ncol in enumerate(names):
        d = np.array( [data[nrow], data[ncol]] )
        dd.append(d)
dd = tuple(dd)

#  create the figure
f = plot_array(dd, names)

# invoke the brusher
B = Brusher(f, dd)

# show it!
plt.show()



