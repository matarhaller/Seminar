#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 8 Solutions
Author: Christopher Klein
"""
# Import GUI modules from enthought
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.api import ImageResource
from enthought.traits.api import Any, Instance
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.basic_editor_factory import BasicEditorFactory
# To parse the Google image search, we will use simplejson (can easy_install)
# http://pypi.python.org/pypi/simplejson/
import simplejson
# We'll use urllib to encode the search url and 
# urllib2 to access the images on the web
import urllib, urllib2
# We will be storing the image as an array
from numpy import array
# Use wx and matplotlib to put the image canvas in the GUI
import wx
import matplotlib
# We want matplotlib to use a wxPython backend
# matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
# A few more methods we'll need from pyplot
from matplotlib.pyplot import imread, imshow, draw
# Python Imaging Library imports for image manipulation
import Image, ImageFilter, ImageEnhance

# These first two class definitions come from the mpl_figure_editor.py code 
# supplied with this week's resources to provide a matplotlib canvas embedding
# solution.
# Full example here, in code snippet #8:
#  http://code.enthought.com/projects/traits/docs/html/tutorials/traits_ui_scientific_app.html
class _MPLFigureEditor(Editor):
    scrollable  = True
    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()
    def update_editor(self):
        pass
    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        return panel
class MPLFigureEditor(BasicEditorFactory):
    klass = _MPLFigureEditor

# We're using Traits, so we define a class which inherits from HasTraits and 
# this will be what we use to create the GUI and give it functionality. To 
# actually run the GUI, we'll create an instance of this class (call it app) in 
# the main function and then call app.configure_traits() to popup the GUI.
class Application(HasTraits):
    """ Aplication object """
    # Here we create and originally specify the contents of our GUI.
    # We want a string that the user will set to store the query. We set a 
    # default value, but this is not strictly necessary.
    query_string =  CStr("Monty Python, humour", desc="image query string")
    # Use a button to allow the user to manually run the query. This is 
    # necessary because the program won't know when the query string is fully 
    # specified and it would be silly to run the query each time the user 
    # altered the query string (each time he/she typed or deleted anohter 
    # letter.)
    run_query = Button()
    # We will display the image url in a panel, so define it now and leave it
    # blank.
    image_url = CStr("", desc="resultant image url")
    # The data of the image will be read into this array so that it can be 
    # displayed in the matplotlib figure.
    im_array = array([])
    # And this is the matplotlib figure.
    figure = Instance(Figure, ())
    # Finally, we define a bunch of buttons which we'll tie to image 
    # manipulation functions exposed by PIL.
    refresh = Button()
    blur = Button()
    sharpen = Button()
    smooth = Button()
    edge = Button()
    contrast = Button()
    color = Button()
    decolor = Button()
    brighten = Button()
    darken = Button()
    
    def display_image(self):
    # Simple function to read the data from image.jpg and redraw the matplotlib
    # figure canvas. Note that in this solution we're writing out the image to
    # the filename image.jpg each time it is altered by PIL. That's why we must
    # re-read the image each time we want to display it in the GUI. It's a work-
    # around for transferring the image from PIL's format to an array. If we 
    # decided to use only numpy/scipy operations on the image, we would not 
    # need to do this.
        self.im_array = imread("image.jpg")#[::-1]
        axes = self.figure.add_subplot(111)
        axes.imshow(self.im_array)
        self.figure.canvas.draw()
    
    def _refresh_fired(self):
    # We store the original image as image_original.jpg and allow the refresh
    # button to restore the image.jpg file and refresh the display.
        print "Refreshing the image!"
        im = Image.open("image_original.jpg")
        im.save("image.jpg", "JPEG")
        self.display_image()
    
    # These next 9 methods all operate on the image with a PIL manipulation 
    # method, write over image.jpg, and then redisplay the result.
    def _blur_fired(self):
        print "Blurring the image!"
        im = Image.open("image.jpg")
        im_blurred = im.filter(ImageFilter.BLUR)
        im_blurred.save("image.jpg", "JPEG")
        self.display_image()
    def _sharpen_fired(self):
        print "Sharpening the image!"
        im = Image.open("image.jpg")
        im_sharpness_enhanced = ImageEnhance.Sharpness(im).enhance(2)
        im_sharpness_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _smooth_fired(self):
        print "Smoothing the image!"
        im = Image.open("image.jpg")
        im_smoothed = im.filter(ImageFilter.SMOOTH_MORE)
        im_smoothed.save("image.jpg", "JPEG")
        self.display_image()
    def _edge_fired(self):
        print "Edging the image!"
        im = Image.open("image.jpg")
        im_edge_enhanced = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
        im_edge_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _contrast_fired(self):
        print "Contrast enhancing the image!"
        im = Image.open("image.jpg")
        im_contrast_enhanced = ImageEnhance.Contrast(im).enhance(2)
        im_contrast_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _color_fired(self):
        print "Color enhancing the image!"
        im = Image.open("image.jpg")
        im_color_enhanced = ImageEnhance.Color(im).enhance(2)
        im_color_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _decolor_fired(self):
        print "Color diminishing the image!"
        im = Image.open("image.jpg")
        im_decolor_enhanced = ImageEnhance.Color(im).enhance(0.5)
        im_decolor_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _brighten_fired(self):
        print "Brightening the image!"
        im = Image.open("image.jpg")
        im_brightness_enhanced = ImageEnhance.Brightness(im).enhance(2)
        im_brightness_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    def _darken_fired(self):
        print "Darkening the image!"
        im = Image.open("image.jpg")
        im_darkness_enhanced = ImageEnhance.Brightness(im).enhance(0.5)
        im_darkness_enhanced.save("image.jpg", "JPEG")
        self.display_image()
    
    def _run_query_fired(self):
        """ Queries Google image search for with the query string """
        # This is where we run the actual query once the user tells the GUI to 
        # do so. We're using the Google api to do a search amd the simplejson
        # to parse the results and get the image urls.
        search_data = {}
        search_data["images"] = self.query_string
        # We encode the search string to append it to the search url.
        url_values = urllib.urlencode(search_data)
        # The search url.
        url = (
            "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" 
            + url_values.lstrip("images="))
        # Run the google search.
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request)
        # Process the JSON string.
        results = simplejson.load(response)
        # The image_url = results['responseData']['results'][0]['url']
        # We make a list of the top 4 image urls.
        imagurl_list = []
        for n in range(4):
           imagurl_list.append(results['responseData']['results'][n]['url'])
        # We will try each image url in succession to download the image. We 
        # need to do this in a complicated control loop because not all image 
        # urls returned from the search still work. We need to try/except 
        # the urllib2 connection errors and check that the image url linked to 
        # a valid image we can download. If not, move on to the next url. If 
        # no image urls were returned in the search (for example, if the search
        # was too specific and returned no results), print an explanation 
        # in the GUI by writing it into the image_url string.
        final_imgurl = False
        for imgurl in imagurl_list:
            print "Connecting to", imgurl
            error_encountered = False
            try:
                response = urllib2.urlopen(imgurl)
            except:
                error_encountered = True
                print "Oh no, HTTP error encountered on " + imgurl
            if not error_encountered:
                final_imgurl = imgurl
                break
        if final_imgurl:
            print "Successfully accessed", final_imgurl
            self.image_url = final_imgurl
            image_string = response.read()
            response.close()
            image_file = file("image.jpg", "w")
            image_file.write(image_string)
            image_file.close()
            image_file = file("image_original.jpg", "w")
            image_file.write(image_string)
            image_file.close()
            self.display_image()
            print "Retrieved image and saved it as image.jpg"
        else:
            print ("Failed to retrieve any image, no " + 
                "results found.")
            self.image_url = ("Failed to retrieve any image, " + 
                "no results found.")
    
    # User interface views:
    traits_view = View( 
        VGroup( 
            # First group for the query. Set width to something reasonable. In 
            # this solution, the width is actually determined by the row of 
            # buttons on the bottom, since there are so many.
            HGroup( 
                Item('query_string', springy=True, width=500),
                Item('run_query', show_label=False), 
                label='Input',
                show_border=True
            ),
            # Next, print out the image url so that the user knows where the 
            # image came from.
            HGroup(
                Item('image_url', style='readonly', springy=True, 
                    show_label=False),
                label='Image URL',
                show_border=True
            ),
            # Show the actual image in the matplotlib figure. We set a 
            # reasonable height. If the height is too big, the GUI will not be 
            # fully shown on smaller screens.
            HGroup(
                Item('figure', editor=MPLFigureEditor(), show_label=False, 
                    height=480), 
                label='Image Display',
                show_border=True
            ),
            # In the last group put all the buttons for image manipulation.
            HGroup(
                Item('refresh', show_label=False),
                Item('blur', show_label=False),
                Item('sharpen', show_label=False),
                Item('smooth', show_label=False),
                Item('edge', show_label=False),
                Item('contrast', show_label=False),
                Item('color', show_label=False),
                Item('decolor', show_label=False),
                Item('brighten', show_label=False),
                Item('darken', show_label=False),
                label='Image Manipulations Options',
                show_border=True
            ),
        ),
        title   = 'Google Image Search and Manipulation',
        # Include an 'OK' button which just closes down the GUI. This is not 
        # strictly necessary b/c the OS should put similar functionality into 
        # the window frame. Set the whole window to be resizable, and it will 
        # allow the matplotlib figure to expand or contract.
        buttons = ['OK'], resizable=True
    )
    
# Great, now we we run the main we'll get the GUI.
if __name__ == "__main__":
    app = Application()
    app.configure_traits()