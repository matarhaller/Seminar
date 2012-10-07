import aifc
import pylab
import scipy
import numpy as np
import matplotlib.pyplot as plt

#open file
wf = aifc.open('/Users/matar/Documents/Courses/python-seminar/Homeworks/homework4_data/F4_CathedralOrgan.aif', 'rb')

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
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(time,data_int)
ax1.set_xlim(min(time), max(time))
ax1.set_xlabel("Time [ms]")
ax1.set_ylabel("Amplitude")

##fft
npoints = np.ceil((n+1)/2.0) #number of unique timepoints (single sided)
data_fft = scipy.fft(data_int) #compute fft
data_fft = data_fft[0:npoints]
Y = abs(data_fft)
Y = Y/float(n) #normalize by length

freqs = np.arange(0, npoints, 1.0) * (srate / float(n))

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(freqs, abs(Y),color = 'r')

#calculate power spectral density
Y = Y**2 #square for power

if n % 2 > 0: #odd fft
	Y[1:len(Y) - 1] = Y[1:len(Y)]*2
else:
	Y[1:len(Y)-1] = Y[1:len(Y)-1]*2


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(freqs/1000, 10*np.log10(Y), color='g')
ax1.set_xlabel('Frequency (kHz)')
ax1.set_ylabel('Power (dB)')
plt.show()


pwr,fq = mlab.psd(data_int,Fs=srate)
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(fq,pwr)