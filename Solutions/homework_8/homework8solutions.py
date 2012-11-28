'''
Solutions to PySci Parallelism Homework
Fall 2012

Author: Isaac Shivvers
'''

###############################################
# imports
from time import time, sleep
from random import uniform
from math import sqrt
import numpy as np
import multiprocessing as mp
from subprocess import Popen
from IPython import parallel as iparallel


###############################################
# function definitions

# I split the approximation into two functions, so that we can
#  utilize the multiprocessing capabilities most effectively
def simulation(number_of_darts = 200000):
    '''
    run a simulation of throwing darts at a circle inside a square.
    used to approximate pi.
    '''
    number_of_hits = 0
    for n in range(number_of_darts):
        x,y = uniform(0, 1), uniform(0, 1) # throw a dart
        if sqrt( (x-.5)**2 + (y-.5)**2 ) <=.5:
            # we got one in the circle!
            number_of_hits += 1
    return number_of_hits, number_of_darts

def pi_from_sim( nhits, nthrows ):
    # the area of our circle: A = pi * .5**2
    #  our approximation: A_circle / A_square = number_of_hits / number_of_darts
    #  therefore, we get an approximation of pi:
    #  pi ~ 4 * (number_of_hits/number_of_darts)
    pi_approx = 4. * float(nhits)/nthrows
    return pi_approx


###############################################
# main script starts here
###############################################

# define how many darts to throw for each simulation
darts_thrown = map(int, np.logspace(1, 7, 10))
# define how many times to run each simulation, to get standard deviations
#  and make a better plot
n_runs = 5

###############################################
# run the simulation normally:
print 'starting serial evaluation...'
times_array = []
for iii in range(n_runs):
    times = []
    for ndarts in darts_thrown:
        t_start = time()
        rez = simulation(ndarts)
        pi_approx = pi_from_sim(*rez)
        t_execute = time()-t_start
        times.append(t_execute)
    times_array.append(times)

# put the set of recorded times into an array for easy manipulation
times_array = np.array(times_array)
# now get the mean and standard deviation from the set of trials
l = len(times_array[0])
mean_times_s = np.array(map( lambda x: np.mean(x), [times_array[:,i] for i in range(l)]) )
std_times_s = np.array(map( lambda x: np.std(x), [times_array[:,i] for i in range(l)]) )


###############################################
# run the simulation using multiprocessing
print '\n\nstarting multiprocessing evaluation...'
n_cores = mp.cpu_count()  # use all the cpus you have
pool = mp.Pool( processes=n_cores )

# Divide each simulation amongst your cores, running a set of 
#  smaller simulations and accumulating their results.  Note
#  that the multiprocessing Pool.apply() function only submits
#  the job to one of the workers in the pool, so we have to 
#  submit a job for each core in our pool.
times_array = []
for iii in range(n_runs):
    times = []
    for ndarts in darts_thrown:
        # divide the darts amongst the cores
        ndarts_each = ndarts/n_cores
        t_start = time()
        results = []
        # submit all of the jobs
        for n in range(n_cores):
            async_result = pool.apply_async( simulation, args=(ndarts_each,) )
            results.append( async_result )
        # now, wait for and collect the results:
        total_hits, total_throws = 0, 0
        for r in results:
            nhit, nthrow = r.get()
            total_hits += nhit
            total_throws += nthrow
        pi_approx = pi_from_sim( total_hits, total_throws )
        t_execute = time()-t_start
        times.append(t_execute)
    times_array.append(times)

times_array = np.array(times_array)
l = len(times_array[0])
mean_times_mp = np.array(map( lambda x: np.mean(x), [times_array[:,i] for i in range(l)]) )
std_times_mp = np.array(map( lambda x: np.std(x), [times_array[:,i] for i in range(l)]) )
    
###############################################
# run the simulation using IPython Parallel
print '\n\nstarting IPython parallel evaluation...'

# first, start a cluster running in the background, and give
#  it a few seconds to initialize
o = Popen('ipcluster start -n {}'.format(n_cores), shell=True)
print 'waiting for engines to start'
sleep(10) # increase this if the cluster doesn't start in time
rc = iparallel.Client()

# for IPython parallel, we need to make all of our imports
#  on each core
import_string = '''
from random import uniform
from math import sqrt
from time import time'''
rc[:].execute(import_string)

# now we run the parallel simulations in a similar fashion to the above,
#  but with slightly different syntax.
times_array = []
for iii in range(n_runs):
    times = []
    for ndarts in darts_thrown:
        ndarts_each = ndarts/n_cores
        t_start = time()
        sync_result = rc[:].apply_sync( simulation, ndarts_each )
        nhits, nthrows = zip(*sync_result)
        pi_approx = pi_from_sim( sum(nhits), sum(nthrows) )
        t_execute = time()-t_start
        times.append(t_execute)
    times_array.append(times)


times_array = np.array(times_array)
l = len(times_array[0])
mean_times_ip = np.array(map( lambda x: np.mean(x), [times_array[:,i] for i in range(l)]) )
std_times_ip = np.array(map( lambda x: np.std(x), [times_array[:,i] for i in range(l)]) )

# do some cleanup, and stop the IPython parallel cores
o = Popen('ipcluster stop', shell=True)



###############################################
# now build our pretty plot
import matplotlib.pyplot as plt

# use the twinx() function to show two different plots on the same x axis
ax1 = plt.subplot(111)
ax2 = ax1.twinx()

# go through and build each line
#  we plot the mean and standarde deviation of the execution time on one axis,
#  and the average dart-throwing rate on the other axis
labels = ['Simple', 'Multiprocessing', 'IPcluster']
time_arrays = [mean_times_s, mean_times_mp, mean_times_ip]
std_arrays = [std_times_s, std_times_mp, std_times_ip]
colors = ['r','c','g']
for i in range(3):
    ax1.loglog( darts_thrown, time_arrays[i], label=labels[i], c=colors[i], lw=2)
    ax1.fill_between( darts_thrown, time_arrays[i]+std_arrays[i], time_arrays[i]-std_arrays[i], alpha=.3, color=colors[i])
    rate = darts_thrown/np.array(time_arrays[i])
    ax2.loglog( darts_thrown, rate, ls='--', c=colors[i], lw=2)

ax1.legend(loc='best')
ax1.set_xlabel('Darts Thrown')
ax1.set_ylabel('Execution Time (seconds), solid line')
ax2.set_ylabel('Simulation Rate (darts/second), dashed line')
plt.show()



