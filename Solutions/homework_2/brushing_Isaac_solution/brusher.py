'''
Contains Brusher class, for homework 2, PySci Fall 2012

Usage:
>>> from brusher import Brusher
>>> B = Brusher(figure, data)
>>> plt.show()
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class Brusher():
    '''
    A generic brusher.
    
    Expects:
    fig:  a mpl figure with subplots
      NOTE: each individual point, in each subplot, must be assigned its own color.
            e.g. use `scatter(x_coords, y_coords, c=array_of_rgba_colors)`
    data: a tuple of numpy arrays, with one entry for each axis in fig, in order (i.e. left->right then top->bottom)
      each item in the tuple must by a 2d numpy array with:
      array[0] --> 1d array of x coordinates
      array[1] --> 1d array of y coordinates
      and each list must be in the same order.
      i.e. the nth pair of values in the first array of the tuple must correspond
           to the nth pair of values in every other array in the tuple.
    '''
    
    def __init__(self, fig, data):
        '''
        fig:  a pre-rendered figure, with subplot axes
        data: the data represented in fig, formatted as described above
        '''
        self.fig  = fig
        self.data = data
        self.axl  = fig.get_axes()
        
        # internal things to keep track of
        self.button_down = False
        self.brush       = None
        self.brush_axis  = None
        self.start_xy    = (None, None)
        
        # define the colors we want to use (overwrites original figure's colors)
        self.unbrushed_color = [.5, .5, .5, .5]  # this is a transparent gray
        self.brushed_color   = [0., 0., 1., .75]  # this is a transparent blue

        # register events to track
        self.fig.canvas.mpl_connect('button_press_event', self.button_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.button_release)


    def button_press(self, event):
        ''' handles a mouse click '''
        # if clicked outside of axes, ignore
        if not event.inaxes: return

        # remove old brush object if it's there
        if self.brush:
            self.brush.remove()
            self.unbrush_me()
            plt.draw()
    
        # start a brush here
        self.button_down = True
        self.start_xy    = (event.xdata,event.ydata)
        self.brush       = Rectangle( self.start_xy, 0,0, facecolor='gray', alpha=.15 )
        self.brush_axis  = event.inaxes
        
        # add brush to axis
        event.inaxes.add_patch(self.brush)
        plt.draw()
        
        
    def mouse_motion(self, event):
        ''' handles the mouse moving around '''
        # if we haven't already clicked and started a brush, ignore the motion
        if not (self.button_down and self.brush): return
        # if we've moved the mouse outside the starting axis, ignore
        if self.brush_axis != event.inaxes: return

        # otherwise, track the motion and update the brush
        self.brush.set_width( abs(self.start_xy[0] - event.xdata) )
        self.brush.set_height( abs(self.start_xy[1] - event.ydata) )
        self.brush.set_x( min(self.start_xy[0], event.xdata) )
        self.brush.set_y( min(self.start_xy[1], event.ydata) )
        plt.draw()


    def button_release(self, event):
        ''' handles a mouse button release '''
        self.button_down = False
        
        # if we didn't start with a brush, ignore
        if not self.brush: return
        
        # if we just clicked without drawing, remove the brush
        if (event.xdata, event.ydata) == self.start_xy:
            self.unbrush_me()
            plt.draw()
            return
        
        # if we stopped inside the same axis, update the brush one last time
        if event.inaxes == self.brush_axis:
            self.brush.set_width( abs(self.start_xy[0] - event.xdata) )
            self.brush.set_height( abs(self.start_xy[1] - event.ydata) )
            self.brush.set_x( min(self.start_xy[0], event.xdata) )
            self.brush.set_y( min(self.start_xy[1], event.ydata) )
        
        self.brush_me()
        plt.draw()
        
        
    def brush_me(self):
        ''' apply the new brush to data in all axes '''
        # figure out the indices of the data inside the brush
        i_brush_axis = self.axl.index(self.brush_axis)
        ax_data = self.data[i_brush_axis]
        bbox    = self.brush.get_bbox()
        boolean_brushed = []
        for i in range(len(ax_data[0])):
            if bbox.contains( ax_data[0,i], ax_data[1,i] ):
                boolean_brushed.append(True)
            else:
                boolean_brushed.append(False)
        boolean_brushed  = np.array(boolean_brushed)
        # boolean_brushed is an array of T,F values indicating whether the datapoint at
        #  that index should be 'brushed' (i.e. keep its color) or not (made gray)
        
        for i, ax in enumerate(self.axl):
            plotted_things = ax.collections[0]
            # now set the facecolor of all points not brushed to gray
            #  new_fc is a 2d array, the 0th axis corresponding to individual points,
            #  and the 1st axis corresponding to color values
            new_fc = plotted_things.get_facecolors()
            new_fc[~boolean_brushed] = self.unbrushed_color
            new_fc[boolean_brushed]  = self.brushed_color
    
    
    def unbrush_me(self):
        ''' paint everything the brushed color '''
        # build an always-true boolean array and brush to that
        boolean_brushed = []
        for i in range(len(self.data[0][0])):
            boolean_brushed.append(True)
        boolean_brushed = np.array(boolean_brushed)
        for i, ax in enumerate(self.axl):
            plotted_things = ax.collections[0]
            new_fc = plotted_things.get_facecolors()
            new_fc[boolean_brushed]  = self.brushed_color
        