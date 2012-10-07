import aifc
import pylab
import scipy
import numpy as np
import matplotlib.pyplot as plt
import urllib2
from bs4 import BeautifulSoup
from matplotlib import mlab
import argparse

def get_soundfile(filename,dplot = 1):
	"""
	reads in the acii file, optionally plots
	"""
	#open file
	wf = aifc.open(filename, 'rb')

	#read data
	data = wf.readframes(wf.getnframes())
	srate = wf.getframerate()

	#close file
	wf.close()

	#format data, time
	data_int = pylab.fromstring(data,dtype=np.int32)
	n = data_int.size
	time = np.arange(n)/float(srate)
	time = time*1000 #ms

	#plot sound file
	if dplot:
		fig = plt.figure()
		ax1 = fig.add_subplot(1,1,1)
		ax1.plot(time,data_int)
		ax1.set_xlim(min(time), max(time))
		ax1.set_xlabel("Time [ms]")
		ax1.set_ylabel("Amplitude")

	return data_int, srate

def get_peakfreq(data,srate,dplot = 1):
	##fft
	n = data.size
	npoints = np.ceil((n+1)/2.0) #number of unique timepoints (single sided)
	data_fft = scipy.fft(data) #compute fft
	data_fft = data_fft[0:npoints]
	Y = abs(data_fft)
	Y = Y/float(n) #normalize by length

	##find peak freq
	freqs = np.arange(0, npoints, 1.0) * (srate / float(n))
	maxfreq = freqs[mlab.find(Y==max(Y))][0]

	if dplot:
		#plot fft
		fig = plt.figure()
		ax1 = fig.add_subplot(1,1,1)
		#ax1.plot(freqs/1000, 10*np.log10(Y), color='g')
		ax1.plot(freqs,Y,color='m')
		ax1.set_xlabel('Frequency (kHz)')
		ax1.set_ylabel('Power (dB)')
		plt.show()

	##find fundamental freq
	return maxfreq

def make_notedict():
	#lookup table
	response = urllib2.urlopen("http://www.contrabass.com/pages/frequency.html")
	#response = urllib2.urlopen('http://www.phy.mtu.edu/~suits/notefreqs.html')
	html = response.read()
	response.close()

	page = BeautifulSoup(html)

	header = ["note","frequency","comments","lowest note", "highest note"]
	notedict = {}

	for key in header:
		notedict[key] = []

	for tablerow in [x.findAll("td") for x in page.find('tbody').find_all('tr')[2:]]:
		datalist = [val.get_text() for val in tablerow]
		for idx, key in enumerate (header):
			try:
				notedict[key].append(float(datalist[idx]))
			except:
				notedict[key].append(datalist[idx])

	return notedict

def get_note(freq):
	notedict = make_notedict()

	freqs = notedict['frequency']

	diffs = abs(freqs-freq)

	idx = mlab.find(diffs== min(diffs))

	return notedict['note'][idx]


def answer_hw(filename,dplot):
	print "-"*40
	print "question 2 - notes"

	data, srate = get_soundfile(filename,dplot)
	maxfreq = get_peakfreq(data,srate,dplot)
	note = get_note(maxfreq)
	print "the note is" + note
	print "harmonics not accounted for"


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "HW4 from the command line")
	parser.add_argument('-s', action = 'store', dest = 'inputstr', help = 'full path to music file')	
	parser.add_argument('-i', action = 'store', dest = 'dplot', help = 'whether or not to plot')
	args = parser.parse_args()
	print answer_hw(args.inputstr, args.dplot)