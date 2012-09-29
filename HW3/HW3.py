from __future__ import division
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import math

def rejsampler1d(target,ref,numsamples):
	"""
	Inputs: functional form of  target distribution, 
			reference distribution in the form of a scipy.stats object (e.g. scipy.stats.norm(0,1))
			number of samples desired. 
	Output: the samples, the value of M, and the proportion of samples that was accepted.
	"""
	samples = list()
	tries = 0
	M = findM(target,ref)

	while len(samples) < numsamples:
		xc = ref.rvs()
		u = stats.uniform.rvs()	
		if (u < (target(xc)/(M*ref.pdf(xc)))):
			samples.append(xc)
		tries +=1

	successrate = numsamples/tries
	return samples, M, successrate


def findM(target,ref):
	x = np.linspace(-6,6)
	return max(ref.pdf(x)/target(x))


def mytargetfunc(x):
	return (0.9**((abs(x**2))))/.6


def answer_hw():
	##question a
	print '-'*40
	print "question a : rejsampler1d defined"
	print '-'*40
	

	##question b
	print '-'*40
	print "question b: cauchy as reference for laplace"
	print '-'*40

	ref = stats.cauchy(0,1)
	target = stats.laplace(0,1).pdf
	numsamples = 1000
	samples, M, successrate = rejsampler1d(target,ref,numsamples)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	n,bins,patches = ax.hist(samples,100,alpha = 0.75,normed = True,label='Laplace distribution')
	actual = stats.laplace.pdf(np.linspace(-6,6,100))
	ax.plot(np.linspace(-6,6,100),actual,'r',label ='Cauchy distribution')
	plt.legend()

	KStest = stats.kstest(samples,'laplace',(0,1))
	print "Kolmogorov-Smirnov test statistic : %f \np-value : %f " %(KStest)
	if KStest[1]>=0.05:
		keyword = 'not'
	else:
		keyword = ""
	print "samples are %s from laplace(0,1) distribution" %(keyword)

	##question c
	print '-'*40
	print "question c: t distribution with df =2 as reference for laplace"
	print '-'*40
	
	ref = stats.t(2)
	target = stats.laplace(0,1).pdf
	numsamples = 1000
	samples, M, successrate_student = rejsampler1d(target,ref,numsamples)
	if successrate_student < successrate:
		keyword = 'better'
	else:
		keyword = 'worse'
	print "acceptance rate is %f \n" %(successrate)
	print "using student's t distribution for reference is %s than using a cauchy distribution" %(keyword)

	##question d
	print '-'*40
	print "question d: novel continuous distribution"
	print '-'*40
	ref = stats.norm(0,2)
	target = mytargetfunc
	numsamples = 5000
	samples, M, successrate = rejsampler1d(target,ref,numsamples)
	#plot figure
	fig = plt.figure()
	ax = fig.add_subplot(111)
	n,bins,patches = ax.hist(samples,100,alpha = 0.75,normed = True,label = 'target function')
	actual = target(np.linspace(-6,6,100))
	ax.plot(np.linspace(-6,6,100),actual,'r',label = 'normal distribution')
	plt.legend()









