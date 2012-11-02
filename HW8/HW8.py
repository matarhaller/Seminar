"""
need to call:
ipcluster start -n 4 outside of python
"""

from multiprocessing import Pool
from IPython import parallel
import numpy as np

def serial(number_of_darts = 200000):
	"""
	serial dart throwing simulation
	input is the total number of darts to throw
	returns a dictionary with parameters of simulation:
	pi_approx, number_of_darts,execution_time,number_of_darts_in_circle
	"""
	from random import uniform
	from math import sqrt
	from time import time

	#Define a varialbe to store the number of darts that fall inside the circle
	number_of_darts_in_circle = 0

	#Use time() to record the execution time of the loop that runs the dart throwing simulation
	start_time = time()

	#This loop simulates the dart throwing. For each dart, find a random position in the unit square for it to fall. Test if it falls within the circle by calculating the distance from the origin (.5, .5) to the dart. Darts that fall within 0.5 of the origin are within the circle.
	for n in range(number_of_darts):
		x, y = uniform(0,1), uniform(0,1)
		if sqrt((x-.5)**2 + (y-.5)**2) <0.5:
			number_of_darts_in_circle+=1

	#Record the time after the conclusion of the loop
	end_time = time()
	#The total time required to run the loop is the difference
	execution_time = end_time - start_time

	#Can calculate an approximate numerical value for pi using the formula for the area of a circle (A = pi * r**2). Here r = 0.5 and the area of the circle can be approximated by the ratio of the number of darts that fall inside the circle over the total number of darts thrown. So pi = 4*A
	pi_approx = 4 * number_of_darts_in_circle/float(number_of_darts)

	#Return dictionary of summary info. Execution time should increase with increasing number of darts. Darts thrown per second should stay relatively constant and is a sort of measure of the speed of the processor
	serial = {'pi_approx' : pi_approx, 'number_of_darts': number_of_darts, 'execution_time' : execution_time, 'number_of_darts_in_circle':number_of_darts_in_circle, "darts_per_second" : number_of_darts/execution_time}
	return serial

def ipcluster_parallel(dview,number_of_darts=200000):
	"""
	calls serial dart throwing on separate engines by scattering the number of darts thrown across them.
	input is the client and (optionally) the number of darts
	returns a list of dictionaries - one dictionary per engine.
	"""
	#put function on all engines
	dview['serial'] = serial 
	#separate darts across engines
	dview.scatter('darts',np.arange(number_of_darts)) 
	#apply serial to length of dart arrays (to get to the total num of darts)
	ser = dview.execute('ans = serial(len(darts))') 
	result = dview.gather('ans',block=True) #list of serial dictionaries
	return result

def ave_parallel_results(results):
	"""
	takes a dictionary of serial results outputted from parallel_ipython. Computes the mean of execution time, pi approximation. Computes the sum of darts per second, number of darts thrown and darts in circle. Makes sense to compute sum of darts per second, althought it makes IPcluster an order of magnitude above the other methods.
	"""
	meandict = dict()
	params = results[0].keys()
	for k in params:
		if k == 'execution_time' or k=='pi_approx':
			meandict[k] = sum([x[k] for x in results])/len(results)
		else:
			meandict[k] = sum([x[k] for x in results])
	return meandict

def multiproc(pool,number_of_darts):
	"""
	multiprocessing code - set up pool of processes
	"""
	result = pool.apply_async(serial,[number_of_darts])
	return result.get()


def run_parallel_methods(dview, pool, dart_array=np.arange(10000,100000,10000)):
	"""
	runs each of the methods (serial, ipython parallel, and multiprocessing) on an array of number of darts.
	returns three lists of dictionaries - each dictionary is for a different number of darts.
	"""
	#subprocess.call(["ipcluster", "start",'-n','4']) <- this works but then doesn't let you do anything else on that terminal. not sure if there is a better way of doing this.
	slist = list()
	plist = list()
	mlist = list()	

	slist = map(serial,dart_array) 
	#for serial, number of darts is lower in map than in loop - why?
	for number_of_darts in dart_array: 
		presults = ave_parallel_results(ipcluster_parallel(dview,number_of_darts))
		plist.append(presults) #ipcluster
		mlist.append(multiproc(pool,number_of_darts)) #multiprocessing
	return slist, plist, mlist


if __name__ == '__main__':

	#set up client for IPcluster
	rc =parallel.Client()
	dview = rc[:]
	#set up the procesess for multiprocessing
	pool = Pool(processes=8)

	dart_array = 10**np.arange(3,8)
	slist, plist, mlist = run_parallel_methods(dview, pool, dart_array)

	import pylab
	import matplotlib.pyplot as plt

	#get the number of darts used - same for all lists - same as dart_array
	#ndarts = np.array([x['number_of_darts'] for x in slist]) 
	ndarts = dart_array

	f = plt.figure(figsize=(11,8), facecolor='w',edgecolor='w')
	ax1 = plt.subplot(111)
	ax2 = ax1.twinx()
	ax1.set_xlabel('Log(Number of Darts Thrown)')
	ax1.set_ylabel('Log(Execution Time), solid line')
	ax2.set_ylabel('Simulation Rate (Darts/Second), dotted line')
	listtype = ['Simple Method','IPcluster Method','Multiprocessing Method']
	
	cnt = 0
	for xlist in [slist, plist, mlist]:
		extime = np.array([x['execution_time'] for x in xlist])
		simtime = np.array([x['darts_per_second'] for x in xlist])
		ax1.plot(ndarts,extime, label = listtype[cnt],linewidth = 2)
		ax2.plot(ndarts,simtime, '--',label = listtype[cnt],linewidth = 2)
		cnt+=1

	ax1.legend(loc='upper left')
	ax1.set_yscale('log')
	ax1.set_xscale('log')
	ax2.set_xscale('log')
	ax1.axis(xmin=10, xmax=10**8)
	ax2.axis(xmin=10, xmax=10**8)
	plt.show()

