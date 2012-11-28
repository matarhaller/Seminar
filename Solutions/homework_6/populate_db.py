'''
Part of the Data(de)basing the 2012 Election homework
solutions, PySci Fall 2012.

Author: Isaac Shivvers


This program scours the web for all of the information we need 
for the homework and coerces it into a sqlite3 database called
`election2012.db`

This should be run first, before the analysis script.
'''

#### IMPORTS
from bs4 import BeautifulSoup
import urllib2, sqlite3
####

# first, remove old versions of election2012.db from disk
#  note, this is here just as a clean up, in case you run this program
#  multiple times.
from os import system
system('rm election2012.db')

# initialize our table
connection = sqlite3.connect("election2012.db")
cursor = connection.cursor()
# create the elections table
sql_cmd = """ CREATE TABLE election (id INTEGER PRIMARY KEY AUTOINCREMENT, state TEXT, contractID INTEGER,
who TEXT, electoral INTEGER)"""
cursor.execute(sql_cmd)
# now create the prediction table
#  I've chosen to format the predictions with one row for every record. For example:
#  id | contractID |   date   | price
#   0 |     745712 | 09/27/12 |  10.0
sql_cmd = """ CREATE TABLE prediction (id INTEGER PRIMARY KEY AUTOINCREMENT, contractID INTEGER, date DATE, price FLOAT)"""
cursor.execute(sql_cmd)


# Now, go out and retrieve the electoral college votes for each state
print 'scraping the web for electoral college numbers...'
# found the below website with some google-fu
url = 'http://www.archives.gov/federal-register/electoral-college/votes/2000_2005.html'
html_str = urllib2.urlopen(url).read()
soup = BeautifulSoup(html_str)
tab = soup.find_all('table')[-1] # choose the relevant table
rows = tab.find_all('tr')

# now go through and populate the election table
#  I keep a list of all the state names, used below when parsing InTrade numbers
#  Here is a good example where keeping the data in pythonic form is probably easier
#  than databasing it, though of course you could do this with sql
states = [] 
for row in rows:
    data = row.find_all('td')
    if len(data) != 6: continue # ignore irrelevant rows
    # a quick way to filter out the rest of the irrelevant rows
    try:
        ecnum = int(data[1].text)
        state = data[0].text
            
        # need two hacks to make the states from this website mesh with the InTrade state names
        if 'Nebraska' in state: state = 'Nebraska'
        if 'District' in state: state = 'District of Columbia (DC)'
        states.append(state)
        # insert this record into the table
        sql_cmd = "INSERT INTO election (state, electoral) VALUES ('%s', %i)" %(state, ecnum)
        cursor.execute(sql_cmd)
    except:
        continue
connection.commit()


# now go through and find all of the intrade contract numbers
#  that correspond to the states above
print 'finding all of the contract IDs from intrade...'
url = 'http://api.intrade.com/jsp/XML/MarketData/XMLForClass.jsp?classID=19'
html_str = urllib2.urlopen(url).read()
soup = BeautifulSoup(html_str)
events = soup.find_all('event')
for event in events:
    # the names of the events of interest are (handily) just the state names
    name = event.find('name').getText()
    if name in states:
        state = name
        dem_c, rep_c = event.find_all('contract')[:2] #discards 'Any other candidate' contracts
        
        # Intrade has multiple seperate contracts for
        #  each of these elections.  One for betting that a
        #  democrat wins, and one for betting that a republican
        #  wins.  I choose whichever one more people have bought into
        #  as the best measure.  This means I need to keep track
        #  of whether this price indicates Prob(Obama wins) or Prob(Romney wins)
        dem_vol = float(dem_c.find('totalvolume').get_text())
        rep_vol = float(rep_c.find('totalvolume').get_text())
        if dem_vol >= rep_vol:
            contract_id = int(dem_c.get('id'))
            who = 'O'
        else:
            contract_id = int(rep_c.get('id'))
            who = 'R'
        
        # update our election table with the contract ID
        sql_cmd = "UPDATE election SET contractID = %i, who = '%s' \
                   WHERE state = '%s'" %(contract_id, who, state)
        cursor.execute(sql_cmd)
connection.commit()


# now populate the prediction table, using the handy intrade API
print 'now pulling down all of the intrade data...'
cursor.execute('SELECT contractID from election')
# reponse is a list of tuples, run a list comprehension to pull out the integer values from the tuples
idlist = [val[0] for val in cursor.fetchall()]
# base url for the API query:
url = 'http://api.intrade.com/jsp/XML/MarketData/ClosingPrice.jsp?conID='
for c_id in idlist:
    html_str = urllib2.urlopen( url+str(c_id) ).read()
    soup = BeautifulSoup(html_str)
    for row in soup.find_all('cp'):
        month, day, year = row.get('date').split(' ')[1].split('/') # format: 7:00AM 12/15/10 GMT --- keep only MM/DD/YY part
        # coerce the date into the format we want
        date = '20{}-{}-{}'.format(year, month, day)
        price = float( row.get('price') )
        # insert into db
        sql_cmd = "INSERT INTO prediction (contractID, date, price) \
                   VALUES (%i, '%s', %d)" %(c_id, date, price)
        cursor.execute(sql_cmd)
connection.commit()

print 'all done!'
