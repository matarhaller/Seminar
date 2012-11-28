#!/usr/bin/env python
"""
AY 250 - Scientific Research Computing with Python
Homework Assignment 4 Solutions
Author: Christopher Klein
"""
import aifc, os, operator
from scipy import optimize
from numpy import fromstring
from matplotlib.pylab import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# This solution makes use of a smoothing code found on the scipy cookbook. It's
# not necessary to use this to identify the notes, but it is an interesting
# approach. The code fragment smoothing.py was found at 
# http://www.scipy.org/Cookbook/SignalSmooth
from smoothing import smooth

# Before diving in, we define some functions for fitting data to a 
# Cauchy-Lorentz distribution. Using scipy.optimize and generalizations of 
# these function defintions one can fit data to any equation. In this case, 
# the power spectrum peaks of the audio are well fit by Cauchy-Lorentz curves.

# Calculate the residual for the Cauchy-Lorentz distribution fit.
def lorentzian_residuals(params, y, x):
    height, g, center_x, offset = params
    err = y - height*((pi * g * (1 + ((x - center_x)/g)**2 ))**-1) - offset
    return err
# Fit the input data with a Cauchy-Lorentz distribution curve.
def fit_lorentzian(y, x, input_params):
    fit_params, success = optimize.leastsq(lorentzian_residuals, input_params, 
        args=(y, x), maxfev=1000)
    return fit_params
# Return a lorentzian curve for a given fit
def lorentzian(x, fit_params):
    height, g, center_x, offset = fit_params
    return height*((pi * g * (1 + ((x - center_x)/g)**2 ))**-1) + offset

# We will run the script in a loop over all the sound files so that we only call
# the script once and it crunches through all the files. A simple way to do this
# is to list all the files in the current directory and run them through the 
# analysis if they are .aif files.
directory = "homework4_data"
file_list = os.listdir(directory)
for input_filename in file_list:
    audio_file_flag = False
    try: 
        if input_filename.split(".")[1] == "aif":
            audio_file_flag = True
        else:
            audio_file_flag = False
    except:
        audio_file_flag = False
    if audio_file_flag:
        print "\nNow analyzing " + input_filename
        # Open the sound file and read the data. The data as read from the file
        # is in string format.
        f = aifc.open(directory + '/' + input_filename, "r")
        data = f.readframes(f.getnframes())
        f.close()
        # We convert the data from string to 16 bit integer.
        #  for this first step, we only read in the first few thousand, so our
        #  plot doesn't explode
        integer_data = fromstring(data, dtype=np.int16)[:10000]
        # We also separate the channels with slicing.
        channel_1 = integer_data[::2]
        channel_2 = integer_data[1:][::2]
        # To improve the signal to noise we can combine the two channels by 
        # averaging their values at each time point.
        new_integer_data = (
            (channel_1.astype(float64) + channel_2.astype(float64)) / 2.0)
        # We store the framerate, which should be 44100.
        framerate = float(f.getframerate())
        # Define an array of the time samples in units of seconds.
        time = arange(size(new_integer_data)) / framerate
        # Now we can dig into the analysis and plotting.
        plot_title = ("AudioAnalysis-" + input_filename.split(".")[0])
        fig = plt.figure(figsize=(15, 12))
        # We will have 3 plots: amplitude vs time, power vs frequency, and 
        # fitted power vs frequency for power spectrum peaks.
        ax1 = fig.add_subplot(3,1,1)
        # The amplitude vs time plot is easy - but we need to downsample it before plotting
        ax1.plot(time, new_integer_data, marker="", color="red", linestyle="-", 
            linewidth=1.5, alpha=1, label="Amplitude")
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Amplitude")
        ax1.set_xlim(min(time), max(time))
        ax1.set_title(plot_title)
        # To generate the power specturm from the data, we will take an FFT. 
        # Before doing so, however, we will regenerate the integer data from
        # the original string, but this time casting to unsigned 32 bit integer.
        # Experimentation with casting to different data types and taking the 
        # FFT found that treating the data like this provided the best note
        # frequency peak detection.
        new_integer_data = fromstring(data, dtype=np.uint32)
        # Taking the Fourier Transform
        n = len(new_integer_data)
        p = fft(new_integer_data) 
        nUniquePts = ceil((n + 1) / 2.0)
        p = p[0:nUniquePts]
        p = abs(p)
        # Scale by the number of points so that the magnitude does not depend on
        # the length of the signal or on its sampling frequency.
        p = p / float(n)
        # Power is amplitude squared.
        p = p**2
        # Deal with the cases of having even and odd numbers of data points.
        if n % 2 > 0: # odd
            p[1:len(p)] = p[1:len(p)] * 2
        else: # even
            p[1:len(p) -1] = p[1:len(p) - 1] * 2
        # Create an array of frequencies, this will be our horizontal axis.
        freqArray = arange(0, nUniquePts, 1.0) * (framerate / n)
        # Define the power in decibels.
        audio_power = 10*log10(p)
        # Here we clip the array data a bit, since human hearing (and hence 
        # possible notes) lie in a subset of these original arrays.
        freqArray = freqArray[100:90000]
        audio_power = audio_power[100:90000]
        # Smooth the power data.
        smoothed_power = smooth(audio_power, window_len=101,window='blackman')
        # Now we can draw the power spectrum plot.
        ax2 = fig.add_subplot(3,1,2)
        ax2.plot(freqArray, audio_power, marker="", color="blue", linestyle="-", 
            linewidth=1.0, alpha=1, label="Power")
        # The raw power spectrum data is pretty ratty, so we overplot with the 
        # smoothed power spectrum, which forms a nicer line.
        ax2.plot(freqArray, smoothed_power, marker="", color="red", 
            linestyle="-", linewidth=1.5, alpha=1, label="Power")
        ax2.set_xlabel("Frequency [Hz]")
        ax2.set_ylabel("Power [dB]")
        # We enforce some reasonable limits. None of the sound files contain
        # fundamental notes beyond the 5th octave.
        ax2.set_xlim(10, 1000)
        ax2.set_ylim(median(audio_power) - 1*std(audio_power), 
            1.05*max(audio_power))
        # The next step is to fit the power spectrum for peaks around musical 
        # notes. A list of the 100 notes, frequencies, and wavelengths was taken
        # from the internet: http://www.phy.mtu.edu/~suits/notefreqs.html
        notes_freqs = []
        notes_file = file("notes_list.txt", "r")
        for line in notes_file:
            # Pull out the note name and frequency.
            notes_freqs.append([line.rstrip().split()[0], 
                float(line.rstrip().split()[1])])
        notes_file.close()
        # Now we go through all the notes and fit each. If a significant peak
        # is detected, we plot the fitted curve in the third subplot and store
        # information about the peak.
        frequency_peaks = []
        ax3 = fig.add_subplot(3,1,3)
        current_note_test = 1
        for note in notes_freqs:
            test_freq = note[1]
            # Localize audio_power and freqArray to fall around test_freq.
            # This step is very important to reducing execution time. There is
            # no point in trying to fit a peak far away from the current note
            # being tested. We do this by figuring out reasonable high and low
            # index values, aiming to include 1000 data points.
            middle_index = int( (test_freq - freqArray[0]) / 
                (freqArray[1] - freqArray[0]) )
            low_index = middle_index - 500
            if low_index < 0: low_index = 0
            high_index = middle_index + 500
            # Store the absolute power peak, which will be used later to 
            # identify the proper notes.
            peak_power = audio_power[middle_index-50:middle_index+50].max()
            # Call the fitting function. The default fit parameters are starting
            # points and the function optimizes to return the best fit.
            fit_params = fit_lorentzian(smoothed_power[low_index:high_index], 
                freqArray[low_index:high_index], [500.0, 10.0, test_freq, 
                median(smoothed_power)])
            # This next line is to indicate progress during testing/development.
            # print note, fit_params, current_note_test
            current_note_test += 1
            # We use the following logical test to determine if a fitted peak is
            # indeed a note. Basically, the fit should be found around the 
            # frequency of the note we're testing, and have reasonably large 
            # height and gamma parameters. We also require that the peak power
            # is at least a 2-sigma outlier.
            if ((abs(fit_params[2] - test_freq) < test_freq/100.0) and 
                fit_params[0]/fit_params[1] > 5 and 
                fit_params[1] < 50 and
                fit_params[1] > 0 and 
                peak_power > (median(audio_power) + 2*std(audio_power))):
                # If it's a good peak, plot it in the third subplot.
                ax3.plot(freqArray, lorentzian(freqArray, fit_params))
                # Finally, if the note currently being tested has not been found
                # as a peak previously, save it for later reporting. Often, 
                # fitting different note locations reduces to the primary peak
                # in that neighborhood, so the actual notes are found multiple
                # times as the full frequency range is explored.
                if test_freq not in frequency_peaks:
                    frequency_peaks.append([test_freq, peak_power])
        # Make up the rest of the plot.
        ax3.set_xlabel("Frequency [Hz]")
        ax3.set_ylabel("Power [dB]")
        ax3.set_xlim(10, 1000)
        ax3.set_ylim(median(audio_power) - 1*std(audio_power), 
            1.05*max(audio_power))
        # And then save it as a png.
        canvas = FigureCanvas(fig)
        canvas.print_figure("AudioAnalysis-" + 
            input_filename.split(".")[0] + ".png", dpi=144)
        # Now that we have a bunch of possible notes, we need to intelligently 
        # identify the primary note(s) and eliminate harmonics. There are 
        # infinite different approaches. Here we place emphasis on 
        # over-reporting. We'd rather have false-positives than false-negatives.
        # What this means is that we would rather incorrectly include a harmonic
        # if it's power peak is significant enough that we cannot fully rule
        # out the possibility that it is also a primary note.
        possible_notes = []
        for frequency in frequency_peaks:
            for note in notes_freqs:
                if abs(frequency[0] - note[1]) < 0.5:
                    possible_notes.append([note[0], note[1], frequency[1]])
        possible_notes_sorted = sorted(possible_notes, 
            key=operator.itemgetter(1), reverse=True)
        # Here we weed out harmonics. To be identified as a harmonic, a 
        # frequency peak must be a multiple of a lower frequency and also 
        # have less than 99% of the power of the fundamental. If the power
        # at a "harmonic" is about equal to or greater than the "fundamental", 
        # then it is possible that they are both played simultaneously.
        harmonic_test_list = sort(append(1.0/(arange(20)+1), (arange(20)+2)))
        confirmed_notes = [possible_notes_sorted.pop()]
        while len(possible_notes_sorted):
            compare_note = possible_notes_sorted.pop()
            harmonic_flag = False
            for current_note in confirmed_notes:
                for test_value in harmonic_test_list:
                    if ((abs((compare_note[1] / current_note[1]) - test_value) < test_value/20) and
                        compare_note[2] < current_note[2]*0.99):
                        harmonic_flag = True
            if not harmonic_flag:
                confirmed_notes.append(compare_note)
        # After creating a final list of confirmed notes, sort them on 
        # increasing frequency and write them out to a final text file.
        confirmed_notes_sorted = sorted(confirmed_notes, 
            key=operator.itemgetter(1), reverse=False)
        print "Writing out notes:"
        output_file = file("note_identifications.txt", "a")
        for note in confirmed_notes_sorted:
            print note
            output_file.write(input_filename.split(".")[0] + "\t" + 
                str(note[0]) + "\t" + str(note[1]) + "\t" + str(note[2]) + "\n")
        output_file.close()
        
