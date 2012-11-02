HW 8 solutions

Should just be able to run HW8.py to generate the figure.

For some reason my figure looks very different from the pdf
The Simple method and MultiProcessing method both have similar simulation rates intitially, while the IPcluster method is way faster. This is because I chose to calculate the simulation rate for the IPcluster as a the mean of the number of darts thrown per second across each of the engines for a given number of darts thrown instead of the sum. If I calculate the sum (which makes no sense, because they are running in parallel), then IPcluster's performance drops to below that of the other two. 

IT looks like the simple method is only marginally slower than the multiprocessing method for this many darts - maybe for larger sizes it makes a bigger difference (but i dont have the patience to run it that long).

I'm running this on a MacBook Pro with 2.66GHz Intel Core i7, with 4 "cores" - maybe I should experiment with more... 
