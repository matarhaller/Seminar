#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 2 problem 2 Solutions
Author: Christopher Klein
"""

from numpy import loadtxt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator
from matplotlib.pylab import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Load in the data
temps = loadtxt("ny_temps.txt", skiprows=1, dtype=int)
yahoo = loadtxt("yahoo_data.txt", skiprows=1, dtype=float)
google = loadtxt("google_data.txt", skiprows=1, dtype=float)

# We want to use hypen instead of unicode minus (better matches the original).
rcParams['axes.unicode_minus'] = False

# We now set up the fonts we will use. Only two fonts are used: Times New Roman 
# and Helvetica. They belong to different families, so we define the font 
# dictionaries to point only to these fonts for each family.
rcParams["font.serif"] = ["Times New Roman"]
rcParams["font.sans-serif"] = ["Helvetica"]
# Then, we create font property objects for each font we want to use. We cannot
# directly affect the font of the tick numbers here, we do that later.
title_font = FontProperties(family="serif", size=30, weight="bold")
axis_label_font = FontProperties(family="sans-serif", size=18)
axis_number_font = FontProperties(family="sans-serif", size=14)
legend_font = FontProperties(family="sans-serif", size=12)

# Figure out the size of the plot. Had to do some guessing and refining until 
# it looked right.
width = 9.34
dim_ratio = 1284./1680.
fig = plt.figure(figsize=(width, width*dim_ratio), dpi=72.0)

# Give it the title, with the above defined font.
fig.suptitle("New York Temperature, Google, and Yahoo!", 
    fontproperties=title_font)
# make the subplot. This will allow us to make an ax2 with a different y axis
# later on.
ax1 = fig.add_subplot(1,1,1)
# Call plot on the stock data. The labels given here are used in the legend.
ax1.plot(yahoo[:,0], yahoo[:,1], marker="", color="purple", linestyle="-",
    linewidth=1.5, alpha=1, label="Yahoo! Stock Value")
ax1.plot(google[:,0], google[:,1], marker="", color="blue", linestyle="-",
    linewidth=1.5, alpha=1, label="Google Stock Value")
# Set x and y labels for the stock data, using the above fonts.
ax1.set_xlabel("Date (MJD)", fontproperties=axis_label_font)
ax1.set_ylabel("Value (Dollars)", fontproperties=axis_label_font)
# Set x and y axis limits for the stock data. Guessing and refinement needed.
ax1.set_xlim(48812.04891304348, 55638.95108695652)
ax1.set_ylim(-22.71689075630252, 772.6168907563025)

# Create a second axis overlaid on the first, with a shared x axis. This is 
# what we use to drop the temperature data with a different y axis.
ax2 = ax1.twinx()
# Call plot on the temperature data.
ax2.plot(temps[:,0], temps[:,1], marker="", color="red", linestyle="--", 
    linewidth=1.5, alpha=1, label="NY Mon. High Temp")
# Set the label and axis limits for the temperature data. Note that to get the 
# correct degree symbol we use unicode.
ax2.set_ylabel(u"Temperture (\u00B0F)", fontproperties=axis_label_font)
ax2.set_xlim(48812.04891304348, 55638.95108695652)
ax2.set_ylim(-150, 100)

# Here we create the legend. Actually, we create two (one for each ax1 and ax2) 
# and then manually line them up. Make the frame white to match the original.
leg1 = ax1.legend(loc=6, prop=legend_font, bbox_to_anchor = (0.00, 0.605), 
    borderpad=0.2, handlelength=3)
leg1_frame = leg1.get_frame()
leg1_frame.set_edgecolor("white")
leg2 = ax2.legend(loc=6, prop=legend_font, bbox_to_anchor = (0.00, 0.535), 
    borderpad=0.2, handlelength=3)
leg2_frame = leg2.get_frame()
leg2_frame.set_edgecolor("white")

# This code draws major and minor tick lines. Major ticks get number labels.
majorLocator_x = MultipleLocator(3333.333333333)
minorLocator_x = MultipleLocator(250)
ax1.xaxis.set_major_locator(majorLocator_x)
ax1.xaxis.set_minor_locator(minorLocator_x)

majorLocator_y1 = MultipleLocator(100)
minorLocator_y1 = MultipleLocator(20)
ax1.yaxis.set_major_locator(majorLocator_y1)
ax1.yaxis.set_minor_locator(minorLocator_y1)

majorLocator_y2 = MultipleLocator(50)
minorLocator_y2 = MultipleLocator(10)
ax2.yaxis.set_major_locator(majorLocator_y2)
ax2.yaxis.set_minor_locator(minorLocator_y2)

# This allows us to set the font size of the tick number labels. 
x_gridlines = ax1.xaxis.get_gridlines()
for tl in ax1.get_xticklabels():
    tl.set_fontsize(12)

# Ok, all done so we write out the image.
canvas = FigureCanvas(fig)
canvas.print_figure("stocks2.png", dpi=72.0)
plt.show()
