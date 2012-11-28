#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 2 Solutions
Author: Christopher Klein
"""

from numpy import array, linspace, exp, where, cos
from scipy import stats, integrate, inf, pi
import pylab

"""(a) is just writing the function."""
def rejection_sampler(  target_distribution_func=stats.laplace.pdf, 
                        reference_distribution=stats.cauchy, 
                        n_samp_goal=1000):
    """ Takes an input a continuous function, the name of a reference 
        distribution and the number of samples to try. Returns an array of the
        accepted samples, the M value uesed, and the acceptance rate.
    """
    samples = []
    samples_tried = 0
    acceptance_rate = 0.5
    # We want to get n_samp_goal number of samples, but we don't know ahead of 
    # time how many we will have to try (we don't know the acceptance_rate 
    # a priori. So, we essentially guess an acceptance rate and then run a 
    # while loop to continue to generate more and more samples until we reach 
    # slighly more than the goal.
    while len(samples) < n_samp_goal:
        n_samp = ((n_samp_goal - len(samples)) / acceptance_rate) + 10
        # x is supposed to be defined for all values. Approximate by setting large
        # limits (-10, 10), but this results in large M and thus a very low
        # acceptance rate (approaching 0).
        x = linspace(-6, 6, 10*n_samp+1)
        f_x = target_distribution_func(x)
        g_x = reference_distribution.pdf(x)
        ratio = f_x/g_x
        M = ratio.max()
        xc = reference_distribution.rvs(size=n_samp)
        g_xc = reference_distribution.pdf(xc)
        f_xc = target_distribution_func(xc)
        u = stats.uniform.rvs(size=n_samp)
        test_ratio = f_xc / (M*g_xc)
        accepted = where(u<test_ratio)
        new_samples = xc[accepted]
        samples = samples + list(new_samples)
        samples_tried += n_samp
    # Once the while loop wraps up, we can calculate the acceptance rate and 
    # truncated down the samples to the n_samp_goal requested.
    acceptance_rate = float(len(samples))/samples_tried
    samples = samples[:int(n_samp_goal)]
    # Return samples as an array, although not strictly necessary
    return array(samples), M, acceptance_rate
    

"""(b)"""

# Define the target distribution as the Laplace(0,1) function.
target_distribution_func = lambda x: (1.0/(2*1.0))*exp(- (abs(x-0.0)/1.0))

# Create the samples.
samples, M, acceptance_rate = rejection_sampler(target_distribution_func, 
                                                reference_distribution=stats.cauchy,
                                                n_samp_goal=1000)
print '#'*20, ' (b) ', '#'*20
print "Results of drawing samples with the Cauchy as reference distribution."
print "M:", M, "Acceptance Rate:", acceptance_rate
# Run the KS Test
D, p_value = stats.kstest(samples,'laplace',(0,1))
print "KS Test finds D=", D, "p-value=", p_value


# Create a value of x to plot the Laplace(0,1) on the histogram.
x = linspace(-4, 4, 10*1000+1)

# We specify the bins to take out ambiguity and ensure that there is a bin 
# centered at 0
my_bins = linspace(-4, 4, 50)

# Create the histgram plot.
n, bins, patches = pylab.hist(samples, bins=my_bins, normed=True, 
                                color="blue", alpha=0.8)
# Overplot the Laplace(0,1) distribution
pylab.plot(x, target_distribution_func(x), linewidth=4, 
                                color="red", alpha=0.8)
# Show the figure.
pylab.show()




"""(c)"""
# Create the samples.
""" The student's t distribution needs a df (degrees of freedom) shape 
    parameter. This is not given in the homework and is not easily added to the 
    function required in part (a).
"""
samples, M, acceptance_rate = rejection_sampler(target_distribution_func, 
                                                reference_distribution=stats.t(2,0),
                                                n_samp_goal=1000)
print '#'*20, ' (c) ', '#'*20
print "Results of drawing samples with the Student's t as reference distribution."
print "M:", M, "Acceptance Rate:", acceptance_rate


"""(d)"""
# Define new, arbitrary continuous distribution. Make sure it is normalized, 
# i.e. that the indefinite integral is equal to 1.
target_distribution_func = lambda x: (cos(pi*(x-.5)) + 1) * exp(-((x-.5)**2)/5) * stats.uniform.pdf((x-.5)+0.5) + (cos(pi*((x-.5)-1)) + 1)*0.95*exp(-(((x-.5)-1.0)**2)/.1) + 1.25*exp(-(((x-.5)-2.0)**2)/.1) + 1.70*exp(-(((x-.5)+1.0)**2)/.1) + 0.25 * exp(-(((x-.5)+1)**2)/2) * stats.uniform.pdf((x-.5)+1.6) + 0.25*exp(-(((x-.5)+2.6)**2)/.3) + 0.55*exp(-(((x-.5)+3.0)**2)/.5)
val, err = integrate.quad(target_distribution_func, -inf, inf, full_output=False)
# Redefine the distribution, now enforcing the normalization.
target_distribution_func = lambda x: (1./val) * ( (cos(pi*(x-.5)) + 1) * exp(-((x-.5)**2)/5) * stats.uniform.pdf((x-.5)+0.5) + (cos(pi*((x-.5)-1)) + 1)*0.95*exp(-(((x-.5)-1.0)**2)/.1) + 1.25*exp(-(((x-.5)-2.0)**2)/.1) + 1.70*exp(-(((x-.5)+1.0)**2)/.1) + 0.25 * exp(-(((x-.5)+1)**2)/2) * stats.uniform.pdf((x-.5)+1.6) + 0.25*exp(-(((x-.5)+2.6)**2)/.3) + 0.55*exp(-(((x-.5)+3.0)**2)/.5) )

# Create the samples.
samples, M, acceptance_rate = rejection_sampler(target_distribution_func, 
                                                reference_distribution=stats.cauchy,
                                                n_samp_goal=5000)
print '#'*20, ' (d) ', '#'*20
print "Results of drawing samples with the Cauchy as reference distribution."
print "M:", M, "Acceptance Rate:", acceptance_rate

# Create a value of x to plot the target_distribution_func on the histogram.
x = linspace(-4, 4, 10*1000+1)

# We specify the bins to take out ambiguity and ensure that there is a bin 
# centered at 0
my_bins = linspace(-4, 4, 50)

# Create the histgram plot.
n, bins, patches = pylab.hist(samples, bins=my_bins, normed=True, 
                                color="blue", alpha=0.8)
# Overplot the Laplace(0,1) distribution
pylab.plot(x, target_distribution_func(x), linewidth=4, 
                                color="red", alpha=0.8)
# Show the figure.
pylab.show()

