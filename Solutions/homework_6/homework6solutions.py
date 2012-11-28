'''
This script answers problems c,d 
from homework 6, PySci Fall 2012

INSTRUCTIONS:
run populate_db.py before running this script!

Author: Isaac Shivvers
'''



import sqlite3
import numpy as np
import matplotlib.pyplot as plt


##################################################
def simulation(probs, weights, cut=0.):
    '''
    probs: array of probabilities (in percent) of succes for each state
    weights: array of electoral college values for each state
    
    cut: all probabilities < cut are guaranteed losses,
         and all probabilitis > (100.-cut) are guaranteed wins.
         (Implemented to answer problem d)
    
    returns: number of electoral college votes won, lost
    '''
    mult = np.empty(len(probs))
    for i,prob in enumerate(probs):
        
        # hacky way to implement cut parameter
        #  if you care about speed, improve this
        if prob > 100.-cut:
            prob = 100.
        elif prob < cut:
            prob = 0.
        
        if 100*np.random.random() < prob:
            mult[i] = 1
        else:
            mult[i] = 0
            
        won = sum(mult*weights)
        total = sum(weights)
    return [won, total-won]


def make_pretty_hist(results, ax):
    ''' create and return formatted histogram of results, and put onto axis '''
    bins = range(0,530)
    total_votes_in_play = results[0,0]+results[0,1]
    obama_loses = results[ results[:,0] < total_votes_in_play/2 ]
    obama_wins = results[ results[:,0] > total_votes_in_play/2 ]
    # put in tests, because at some dates for some cuts there are no simulations where
    #  one of candidates wins
    if len(obama_wins) > 0:
        ax.hist( obama_wins[:,0], bins=bins, color='b', alpha=.7, label='Obama wins' )
    if len(obama_loses) > 0:
        ax.hist( obama_loses[:,0], bins=bins, color='r', alpha=.7, label='Romney wins' )
    x1,x2,y1,y2 = ax.axis() # resize the x axis
    ax.axis( [100, 400, y1, y2])
    ax.annotate('votes in play: {}'.format(int(total_votes_in_play)), (.01,.9), xycoords='axes fraction' )
    ax.set_yticks([]) #remove y-ticks, to make a cleaner plot
    return 
##################################################


##################################################
# MAIN SCRIPT STARTS HERE

# define the number of trial elections to run
number_of_trials = 10000

# open up the database
connection = sqlite3.connect("election2012.db")
cursor = connection.cursor()

# if we've run this before, we already have the results of our simulations
#  saved in the simulation.  Simply use those values!
try:
    cursor.execute("SELECT * FROM simulation")
    already_populated_db = True
except:
    already_populated_db = False


if not already_populated_db:
    # create the new table, into which we will put our simulation results
    sql_cmd = "CREATE TABLE simulation (id INTEGER PRIMARY KEY AUTOINCREMENT, obama_ec_count INTEGER, romney_ec_count INTEGER, date DATE, num_trials INTEGER)"
    cursor.execute(sql_cmd)

    # pull out all of the relevant info for yesterday's results, assuming
    #  you downloaded & built the database sometime today.  This uses modifiers
    #  in the sqlite3 date function: see http://www.sqlite.org/lang_datefunc.html
    sql_cmd = "SELECT prediction.price AS prob, election.who AS who, election.electoral AS electoral_votes \
               FROM prediction JOIN election ON prediction.contractID = election.contractID \
               WHERE prediction.date = DATE('NOW', '-1 day')"
    cursor.execute(sql_cmd)
    out = cursor.fetchall()
    # use the cool zip-star combo to pull out everything from this list of tuples
    #  NOTE: this may fail if you pulled the database more than a day ago!
    #  re-run the database python script if the line below fails.
    probs, who, elec_col = zip(*out)
    # now we have to account for the differences between those records that
    #  are P(Romney wins) and those that are P(Obama wins)
    prob_obama = np.array(probs)
    for i,prob in enumerate(probs):
        if who[i] == 'R':
            prob_obama[i] = 100.-prob

    elec_col = np.array(elec_col) #needs to be in array form for simulation
    # here I do a bit of a funky list comprehension to simulate all of the elections
    #  this could be made to run faster, I'm sure.
    print 'running simulation 1...'
    results = np.array( [simulation(prob_obama, elec_col) for i in range(number_of_trials)] )

    # insert the results into the database
    for i,row in enumerate(results): #number of ec counts for each trial for each candidate
        o_count = row[0]
        r_count = row[1]
        sql_cmd = "INSERT INTO simulation (obama_ec_count, romney_ec_count, date, num_trials) \
                   VALUES (%i, %i, DATE('NOW','-1 day'), %i)" %(o_count, r_count, number_of_trials)
        cursor.execute(sql_cmd)
    connection.commit()


    # make a histogram for all of these simulations
    ax1 = plt.subplot(1,1,1)
    make_pretty_hist(results, ax1)
    plt.title('Current electoral situation')
    plt.ylabel('fraction of simulated elections')
    plt.xlabel('electoral college votes awarded')
    l = plt.legend(loc='upper right')
    l.draw_frame(False)
    plt.show()


    # now do the same as above, but this time for all of the other dates in one fell swoop
    # Note that not all of the states had started a betting pool by July 1, so the number
    #  of electoral college votes up for grabs changes.
    july1 = '2012-07-01'
    sept1 = '2012-09-01'
    oct1 = '2012-10-01'
    dates = [july1, sept1, oct1]
    f, axs = plt.subplots(3,1)
    for j,date in enumerate(dates):
        sql_cmd = "SELECT prediction.price AS prob, election.who AS who, election.electoral AS electoral_votes \
                   FROM prediction JOIN election ON prediction.contractID = election.contractID \
                   WHERE prediction.date = DATE('%s')" %date
        cursor.execute(sql_cmd)
        out = cursor.fetchall()
        probs, who, elec_col = zip(*out)
        prob_obama = np.array(probs)
        for i,prob in enumerate(probs):
            if who[i] == 'R':
                prob_obama[i] = 100.-prob
        elec_col = np.array(elec_col)

        print 'running simulation',j+2,'...'
        results = np.array( [simulation(prob_obama, elec_col) for i in range(number_of_trials)] )
    
        # insert the results into the database
        for i,row in enumerate(results):
            o_count = row[0]
            r_count = row[1]
            sql_cmd = "INSERT INTO simulation (obama_ec_count, romney_ec_count, date, num_trials) \
                       VALUES (%i, %i, '%s', %i)" %(o_count, r_count, date, number_of_trials)
            cursor.execute(sql_cmd)
        connection.commit()
    
        make_pretty_hist(results, axs[j])
        # change the y-axis to show which date we're modeling
        axs[j].set_ylabel(date)

    # annotate the final plot a bit
    axs[0].set_title('The changing electoral landscape')
    l = axs[0].legend(loc='best')
    l.draw_frame(False)
    axs[-1].set_xlabel('electoral college votes awarded')
    plt.show()



# our job is much easier if we've already populated the database
elif already_populated_db:
    print 'loading all values from database...'
    
    sql_cmd = "SELECT obama_ec_count,romney_ec_count FROM simulation WHERE date = DATE('NOW','-1 day')"
    cursor.execute(sql_cmd)
    all_records = cursor.fetchall()
    # unpack the result with the zip-star
    obama_ec, romney_ec = zip(*all_records)
    # coerce these tuples back into the format needed for the pretty histogram function above
    results = np.vstack( (obama_ec, romney_ec) ).T
    
    # make a histogram for all of these simulations
    ax1 = plt.subplot(1,1,1)
    make_pretty_hist(results, ax1)
    plt.title('Current electoral situation')
    plt.ylabel('fraction of simulated elections')
    plt.xlabel('electoral college votes awarded')
    l = plt.legend(loc='upper right')
    l.draw_frame(False)
    plt.show()
    
    
    # now loop through dates and re-create image from database
    july1 = '2012-07-01'
    sept1 = '2012-09-01'
    oct1 = '2012-10-01'
    dates = [july1, sept1, oct1]
    f, axs = plt.subplots(3,1)
    for j,date in enumerate(dates):
        # see above for documentation
        sql_cmd = "SELECT obama_ec_count,romney_ec_count FROM simulation WHERE date = '%s'" %date
        cursor.execute(sql_cmd)
        all_records = cursor.fetchall()
        obama_ec, romney_ec = zip(*all_records)
        results = np.vstack( (obama_ec, romney_ec) ).T
        make_pretty_hist(results, axs[j])
        axs[j].set_ylabel(date)
    # annotate the final plot a bit and show it
    axs[0].set_title("InTrade's changing electoral landscape")
    l = axs[0].legend(loc='upper right')
    l.draw_frame(False)
    axs[-1].set_xlabel('electoral college votes awarded')
    plt.show()
    