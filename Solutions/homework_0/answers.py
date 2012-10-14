'''
Python Computing for Science, Fall 2012

#### Homework 0 Solutions ####
This file uses the bear class (defined in bears.py)
to answer the questions below.

Questions:
a. On average, how many Bears are born in the first 100 years? How many Bears are alive at the end of 150 years?
b. What must be the minimum value of P(male) such that the population does not die out in 150 years?
c. Build and use a plotting routine to show the genealogy tree of a given Bear. Show all Bears at the same generation and earlier who are directly related.
Hints:
- use numpy.random to satisfy your random needs
- use a webservice to build a name generating function - play around with networkx to help you build a genealogy tree

Isaac Shivvers
ishivvers@berkeley.edu
'''

##############################################################
# IMPORTS

from bears import bear
import pickle, random, re, urllib, os, pdb
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from string import ascii_uppercase, ascii_lowercase

##############################################################
# SECONDARY FUNCTION DEFINITIONS

def download_names(page_depth=25):
    ''' 
    Download lists of male and female names from www.listofnames.info
    That website has ~300 names per page, so this function fetches 
    about <page_depth>*300 names for each male and female.
    Returns:
    female_names, male_names  (both lists)
    '''
    print 'pre-fetching names from webservice:'
    f_page_text, m_page_text = '',''
    for i in range(1,page_depth+1):
        print 'downloading page',i
        f_names_page = 'http://www.listofnames.info/find.php?source=feminine&page={}'.format(i)
        m_names_page = 'http://www.listofnames.info/find.php?source=masculine&page={}'.format(i)
        f_page_text += urllib.urlopen(f_names_page).read()
        m_page_text += urllib.urlopen(m_names_page).read()
    # parse those messy text files to search for names, using regular expressions
    #  read up on regular expression syntax to learn more about these - they can be very useful!
    matchstring = '<td>[A-Z][a-z]*\s[A-Z][a-z]*</td>'
    f_names = re.findall(matchstring, f_page_text)
    f_names = [name.strip('<td>').strip('</td>') for name in f_names]
    m_names = re.findall(matchstring, m_page_text)
    m_names = [name.strip('<td>').strip('</td>') for name in m_names]
    print 'found {} female name and {} male names'.format(len(f_names), len(m_names))
    # save and exit
    pickle.dump(f_names, open('female_names.p','w'))
    pickle.dump(m_names, open('male_names.p','w'))

def name_generator(sex):
    '''
    An infinite-loop bear name generator
    which will never give the same name twice.
    '''
    if sex == 'M':
        # test to see if lists of names already exist
        if not os.path.exists('male_names.p'):
            # download and save the names before loading - may take a little while!
            download_names()
        # load saved names
        male_names = pickle.load(open('male_names.p','r'))

        middle_names = False; i = 0
        while True:
            if not middle_names:
                # First yield all of the names from the webservice
                yield male_names[i]
            else:
                # Even with a whole lot of names, we can run out. (Lots of bears.)
                # If this happens, add a middle name.
                # I build a middle name which is a random string of 10 characters.
                # (Who cares about middle names anyways?)
                middle_name = random.sample(ascii_uppercase, 1)[0] + ''.join(random.sample(ascii_lowercase, 9))
                name = male_names[i].split(' ')[0]+' '+middle_name+' '+male_names[i].split(' ')[-1]
                yield name
            i +=1
            # after yielding all the names, start over but add middle names
            if i >= len(male_names):
                i = 0; middle_names = True
    
    elif sex=='F':
        # see comments above for guidance
        if not os.path.exists('female_names.p'):
            download_names()
        female_names = pickle.load(open('female_names.p','r'))

        middle_names = False; i = 0
        while True:
            if not middle_names:
                yield female_names[i]
            else:
                middle_name = random.sample(ascii_uppercase, 1)[0] + ''.join(random.sample(ascii_lowercase, 9))
                name = female_names[i].split(' ')[0]+' '+middle_name+' '+female_names[i].split(' ')[-1]
                yield name
            i +=1
            if i >= len(female_names):
                i = 0; middle_names = True


##############################################################
# MAIN FUNCION

def run_trial(length=150, P_male=.5, geneology_tree_year=0):
    # length: years to run trial
    # P_male: probability of male (vs female) offspring
    # genology_tree_year: year at which to create a geneology tree of
    #  a living bear chosen at random.  If zero, no tree is created
    
    # initialize our name-picking functions
    f_ngen = name_generator('F')
    m_ngen = name_generator('M')
    
    # now build our initial population of bears
    Adam = bear(name='Adam', sex='M', mother='Earth', father='Sun')
    Eve  = bear(name='Eve', sex='F', mother='Venus', father='Sun')
    Mary  = bear(name='Mary', sex='F', mother='Luna', father='Sun')

    bear_population = [Adam, Eve, Mary] #this list contains actual bear objects
    dead_bears = [] # this list will only contian names (memories)
    number_alive = [] # keep track of number of bears alive each year

    # go through and evolve this population!
    for year in range(length):
        # these lists contains actual bear objects
        breeding_male_bears = [animal for animal in bear_population if animal.years_since_procreation >=5 and animal.sex == 'M']
        breeding_female_bears = [animal for animal in bear_population if animal.years_since_procreation >=5 and animal.sex == 'F']

        # provide some feedback
        if year%25 == 0:
            print '#'*50
            print 'entering year',year, 'with', len(bear_population), 'bears, with',len(breeding_male_bears+breeding_female_bears),'breeding.'

        # if you're a breeding bear, try to reproduce
        for animal in breeding_male_bears:
            if len(breeding_female_bears)<1:
                break # I guess there just aren't that many fish in the sea

            # ask female bears (in random order) to make babies.  Isn't that how it works?
            random.shuffle(breeding_female_bears) # this shuffles the list in place
            for other in breeding_female_bears:
                offspring = animal.request_procreation( other ) #returns False if denied
                if offspring:
                    # record the parents
                    mother = other.name
                    father = animal.name
                    # choose a sex and a name
                    if random.random() < P_male:
                        gender = 'M'
                        name = m_ngen.next()
                    else:
                        gender = 'F'
                        name = f_ngen.next()
                    # add this new bear to our population
                    bear_population.append(bear(name=name, sex=gender, mother=mother, father=father))
                    # remove both parents from the breeding lists
                    if animal.sex == 'M':
                        breeding_male_bears.remove(animal)
                        breeding_female_bears.remove(other)
                    break # if you got a baby, stop asking everyone else!
                else:
                    pass  # no offspring, ask another bear...

        # age each bear and test to see if it survived the year
        for animal in bear_population:
            still_alive = animal.age_thyself()
            if not still_alive:
                # another one bites the dust.
                bear_population.remove(animal)
                dead_bears.append(animal.name)
        
        # keep track of number of living bears each year
        number_alive.append(len(bear_population))

        if year>0 and year == geneology_tree_year:
            # create a genealogy tree here, using networkx, but don't show it yet
            G=nx.DiGraph()
            chosen_one = random.sample(bear_population, 1)[0] #select a random bear
            G.add_node(chosen_one.name)
            G.add_edge(chosen_one.mom, chosen_one.name)
            G.add_edge(chosen_one.dad, chosen_one.name)
            # use the pos keyword (see nx.draw below) to structure this tree reasonably
            # parents up on top, main character in the middle, and siblings on the bottom
            pos_dict = {chosen_one.name:(0,1), chosen_one.mom:(0,2), chosen_one.dad:(1,2)}
            # now find other bears who are related,
            # and array them across the bottom using the pos keyword again
            iii = 1
            for other_bear in bear_population:
                if other_bear.name == chosen_one.name: continue
                if other_bear.mom == chosen_one.mom:
                    G.add_edge(chosen_one.mom, other_bear.name)
                    pos_dict[other_bear.name] = (iii,0)
                    iii +=1
                if other_bear.dad == chosen_one.dad:
                    G.add_edge(chosen_one.dad, other_bear.name)
                    pos_dict[other_bear.name] = (iii,0)
                    iii +=1
                if other_bear.dad == chosen_one.dad and other_bear.mom == chosen_one.mom:
                    # put full families on the same level
                    pos_dict[other_bear.name] = (pos_dict[other_bear.name][0], 1)
            # draw the plot now, but don't display it until the end
            nx.draw(G, pos=pos_dict)

        if year == 100:
            # report some statistics
            births_at_100 = len(dead_bears) + len(bear_population) - 3  # excluding the three founders
            print 'at year {}, there are {} living bears'.format(year, len(bear_population))
            print 'there have been {} births, in total'.format( births_at_100 )

    # now report some stats at the end:
    print 'at year {}, there are {} living bears'.format(year, len(bear_population))
    alive_at_150 = len(bear_population)
    if year >= 149:
        return births_at_100, alive_at_150, number_alive #return yearly stats and number_alive array
    else:
        return number_alive #return only number_alive array if we didn't do a full 150-year run


##############################################################
# IF CALLED FROM COMMAND LINE, RUN MAIN FUNCTION

if __name__ == '__main__':
    
    ################ question a ################
    # Run some trial bear populations and report the mean values
    births_at_100, alive_at_150, number_alive = [], [], []
    for iii in xrange(10):
        b100, a150, nalive = run_trial()
        births_at_100.append(b100)
        alive_at_150.append(a150)
        number_alive.append(nalive)
        print '\n'*2, '*'*50, '\n'*2
    # print answer
    print '\nQuestion a:'
    print 'Around {} bears are born in the first 100 years'.format(np.mean(births_at_100))
    print 'and about {} are alive after 150 years.'.format(np.mean(alive_at_150))
    # make plot
    number_alive = np.array(number_alive) # put into numpy array for easy manipulation
    stds = np.array([np.std(number_alive[:,i]) for i in range(len(number_alive[0]))]) #these seem ugly at first, but see if you can figure them out
    means = np.array([np.mean(number_alive[:,i]) for i in range(len(number_alive[0]))])
    # use the super-cool fill_between plot
    x = range(len(means))
    plt.fill_between( x, means+stds, means-stds, alpha=.3 )
    plt.plot( x, means, color='black' )
    plt.xlabel('years')
    plt.ylabel('number of living bears')
    plt.title( 'Average population and standard deviation from {} trials'.format(len(number_alive)) )
    plt.show()
    # wait to move on
    raw_input('\n  press enter to continue \n')
    
    
    ################ question b ################
    # Run up from P_male = 0 until we still have living bears at 150 years.
    # Conduct 5 trials (should run quickly, since we'll have low populations).
    trial_probs = np.linspace(0, 1, 101)
    p_limits = []
    for iii in xrange(5):
        for prob in trial_probs:
            b100, a150, nalive = run_trial(P_male=prob)
            # if we still have any alive, record it!
            if a150:
                p_limits.append(prob)
                break
    # print answer
    print '\nQuestion b:'
    print 'A P(male) of about {} is needed to sustain a population for 150 years.'.format(np.mean(p_limits))
    # wait to move on
    raw_input('\n  press enter to continue \n')
    

    ################ question c ################
    # Run a short population simulation and plot a random bear's current geneology tree
    while True: #in case the population dies out prematurely
        try:
            nalive = run_trial(length=75, geneology_tree_year=70, P_male=.5)
            if nalive[-1] > 0: break
        except:
            pass

    print '\nQuestion c:'
    print 'now plotting geneology tree (for bear in center) at year 70...'
    plt.show()
