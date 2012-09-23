from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.cbook as cbook
import Image
from matplotlib import _png
from matplotlib.offsetbox import OffsetImage
import scipy.io
import pylab

#for question 1 (my data)
def resample(ms,srate):
	return int(round(ms/1000*srate))

def formatdata(data,Params):
	"""
	reads in TrialsMTX data structure, pulls out relevant data
	"""
	mndata = dict()
	alltrials = np.array([])
	for k in range(len(Params["conditions"])):
		conditionmean = data[0,k].mean(axis = 0)
		mndata.update({Params["conditions"][k]: {'data' : data[0,k].mean(axis = 0), 'cmax' : conditionmean.max(), 'cmin' : conditionmean.min()}})
	return mndata

def traces(mndata,Params,srate,imagepath):
	"""
	plots traces of high gamma data for the trial duration. separated by condition, with brain & elec position
	"""
	#plot high gamma traces
	#data should be bandpassed (todo)
	#resample to srate
	st = resample(Params["st"],srate)
	en = resample(Params["en"],srate)
	bl_en = resample(Params["bl_en"],srate)
	bl_st = resample(Params["bl_st"],srate)
	plot_tp = resample(Params["plot"],srate)
	cue = resample(500,srate)
	
	colors = ['red','orange','green','blue']
	x = np.array(range(st,en+1))
	f, (ax,ax2) = plt.subplots(1,2, sharex = False)
	ax.axhline(y = 0,color = 'k',linewidth=2)
	ax.axvline(x = 0,color='k',linewidth=2)
	ax.axvline(x = cue,color = 'gray',linewidth = 2)
	ax.axvline(x = cue+cue,color = 'gray',linewidth = 2)
	ax.axvspan(cue, cue+cue, facecolor='0.5', alpha=0.25,label = 'cue')

	for j in range(len(Params["conditions"])):
		condition = Params['conditions'][j]
		y = mndata[condition]['data']
		ax.plot(x,y, label = condition,linewidth = 2,color = colors[j])
	
	ax.set_ylim((-30,85))
	ax.set_xlim(st,en)
	ax.legend()
	ax.xaxis.set_ticklabels(['', '0', '','500', '', '1000', '', '1500', '', '2000','','2500','', '3000'],minor=False)
	ax.xaxis.set_ticks(range(st,en,plot_tp))

	ax.set_xlabel("time (ms)")
	ax.set_ylabel("% change baseline")
	ax.set_title('Analytic Amplitude - High Gamma (70-150Hz)', fontsize = 18)

	#plot brain with elec location
	#brain = plt.imread(imagepath)
	#aa = pylab.mean(brain,2)
	#ax2.imshow(aa)
	#a2.gray()

	#brain = Image.open(imagepath)
	#ax2.set_axis_off()
	#im = plt.imshow(brain, origin = 'lower')

	#brain = _png.read_png(imagepath)
	#imagebox = OffsetImage(brain,zoom =5)
	#ab = AnnotationBbox(imagebox,)

	im = Image.open(imagepath)
	ax2.imshow(im,aspect = 'auto',origin = 'lower')
	ax2.set_xlim((0,750))
	ax2.set_title('Electrode Location',fontsize = 18)



	return f, (ax, ax2)


#for question 2 (stocks data)
def readdata(filename):
	""" 
	reads in a txt file with 2 columns of numbers and 1 header (dates and values)
	"""
	dt = np.dtype([('date','int'),('val','<f8')])
	data = np.loadtxt(filename,dtype = dt,skiprows = 1)
	return data

def plotstocksdata(datadict,formats):
	"""
	takes in dict of data structures and Params indicating when to start/end
	also takes in formats dictionary. keys must match datadict, values are the linewidth/color to plot
	"""
	#plot data
	f = plt.figure()
	ax1 = plt.subplot(111)
	data = datadict["yahoo"]
	yahoo = ax1.plot(data['date'],data['val'],formats["yahoo"], label = 'Yahoo Stock Value',linewidth = 1.5)
	data = datadict["google"]
	google = ax1.plot(data['date'],data['val'],formats["google"], label = 'Google Stock Value',linewidth = 1.5)
	ax2 = ax1.twinx()
	data = datadict["nytmp"]
	nytmp = ax2.plot(data['date'],data['val'],formats["nytmp"],label = 'NY Mon. High Temp',linewidth=1.5)
	ax1.set_xlabel('Date (MJD)')
	ax1.set_ylabel('Value (Dollars')
	ax1.set_ylim((-20,765))
	ax1.yaxis.set_minor_locator(plt.MultipleLocator(20))
	ax1.set_xlim((48800, 55600))
	ax1.xaxis.set_minor_locator(plt.MultipleLocator(200))
	plt.show()
	ax2.set_ylim((-150, 100))
	ax2.set_ylim((-150, 100))
	ax2.set_ylabel('Temperature  ($^\circ$F)')
	ax2.yaxis.set_minor_locator(plt.MultipleLocator(10))
	plt.title('New York Temperature, Google, and Yahoo!', fontname = 'serif',fontsize = 18)
	plts = yahoo+google+nytmp
	labels = [l.get_label() for l in plts]
	ax1.legend(plts, labels, loc=(0.025,0.5) ,frameon=False, prop={'size':11}, markerscale = 2)
	plt.show()


def answer_hw():
	#QUESTION 1
	#load data
	dataDir = "/Users/matar/Documents/Courses/PythonClass/HW2/data/"
	imagepath = dataDir + 'e37.png'
	matdata = scipy.io.loadmat(dataDir+'TrialsMTX',struct_as_record = True)
	data = matdata["TrialsMTX"]['data'][0,0]

	#define parameters
	Params={"f1":70, "f2": 150, "st" :-250, "en":3000, "plot":250, "bl_st" : -250, "bl_en":0, "caxis":200, "conditions":['20','40','60','80']}
	subjdata = scipy.io.loadmat(dataDir+"subj_globals")
	srate = subjdata["srate"][0,0]

	#format data
	mndata = formatdata(data, Params)

	print '-'*40
	print "question 1 : plotting traces"
	print '-'*40
	traces(mndata,Params,srate,imagepath) 
	#ideally would like to separate the traces func from the brain image, but can't figure out how to plot 2 funcs as subplots of same image


	#QUESTION 2
	formats = {'google' : 'b', 'nytmp' : 'r--', 'yahoo' :'purple'}
	dataDir = "/Users/matar/Documents/Courses/PythonClass/HW2/hw2_data/"
	datadict = {'nytmp': readdata(dataDir+'ny_temps.txt'), 'google': readdata(dataDir+'google_data.txt'), 'yahoo': readdata(dataDir+'yahoo_data.txt')}
	print '-'*40
	print "question 2 : plotting stock data"
	print '-'*40
	plotstocksdata(datadict,formats)