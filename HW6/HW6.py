import sqlite3
from bs4 import BeautifulSoup
import urllib2
import re
import datetime

def urlreader(url):
	response = urllib2.urlopen(url)
	html = response.read()
	response.close()
	page = BeautifulSoup(html)
	return page

def get_elecvotes():
	"""
	makes a dictionary of states with respective electoral votes
	"""
	page = urlreader("http://www.fec.gov/pages/elecvote.htm")
	
	evdict = {}
	for tablerow in [x.findAll("td") for x in page.find('table').find_all('tr')[1:]]:
		datalist = [val.get_text() for val in tablerow]

		try: #because html table has weird blank entries
			state = str(datalist[0])
			votes = float(datalist[-1])
			evdict[state] = votes
		except:
			continue
	DCval = evdict.pop('D.C.')
	evdict['District of Columbia'] = DCval #so that fits with intrade spelling
	return evdict

def get_contractid():
	"""
	a hack for pulling out the contract id for each state from intrade market data.
	there MUST be a better way of doing this
	"""
	page = urlreader("http://api.intrade.com/jsp/XML/MarketData/xml.jsp")
	
	cdict = {}
	evdict = get_elecvotes()
	states = evdict.keys()
	for event in page.findAll('contract'): 
	#can't do as list comprehension because need to be able to refer to event
		name = event.find('name')
		for state in states:
			func = re.compile('Republican nominee to win ' + state)
			blah = func.search(name.string) #if the event name is relevant
			if blah: #if it is, then pull out the contract id
				cid = event.decode().split(' ')[2][3::]
				cid = int(cid[1:-1])
				cdict[state] = cid
	return cdict

def get_closingdata():
	"""
	pull the closing data from the intrade api
	make a dictionary with closing price per date per state
	"""
	cdict = get_contractid()
	cids = cdict.values()
	states = cdict.keys()
	pricedict = {}
	for idx, cid in enumerate(cids):
		state = states[idx]
		pricedict[state] = {}
		url = "http://api.intrade.com/jsp/XML/MarketData/ClosingPrice.jsp?conID=" + str(cid)
		page = urlreader(url)
		data = page.find("closingprice").findAll("cp")
		for cp in data:
			x = cp.decode()
			price = float(x[x.find('price')+7:x.find(" sessionhi")-1])
			date = str(x[x.find('date')+6:x.find(" GMT")])
			#hack to get price and date
			pricedict[state][date] = price
	return pricedict

def answer_hw():
	"""
	answers the hw - makes tables, etc
	"""	
	print "-"*50
	print "question a - create table called 'election' and populate it with statename, electoral votes, and intrade contract id"
	#get data
	evdict = get_elecvotes()
	cdict = get_contractid()
	#make table
	connection = sqlite3.connect("/Users/matar/Documents/Courses/PythonClass/HW6/hw6.db")
	cursor = connection.cursor()
	#define columns
	cmd = """CREATE TABLE election (
		id integer primary key autoincrement default 0,
		state text,
		contractID integer,
		electoral integer
		);"""
	#try:
	#	cursor.execute("DROP TABLE election") 
		#so delete if it already exists so don't get error
	#except:
	cursor.execute(cmd)

	for state in evdict.keys():
		data = (state, evdict[state],cdict[state])
		cmd = ("INSERT INTO election (state,contractID,electoral) VALUES " + str(data))
		cursor.execute(cmd)

	print "-"*50
	print "question b - create a table called 'prediction' and populate it with all of the intrade closing data for each state and general election"
	pricedict = get_closingdata()
	cmd = """CREATE TABLE prediction (
		id integer primary key autoincrement default 0,
		state text,
		day text,
		price integer);"""
	cursor.execute(cmd)

	for state in pricedict.keys():
		for day in pricedict[state].keys():
			price = pricedict[state][day]
			data = (state, day, price)
			cmd = ("INSERT INTO prediction (state, day, price) VALUES " + str(data))
			cursor.execute(cmd)

	#failed attempt to make tables that refer to each other
#	cmd = """CREATE TABLE prediction (
#		id integer primary key autoincrement default 0,
#		state text);"""
#	cursor.execute(cmd)
#
#	cmd = """CREATE TABLE prices (
#		pid integer primary key autoincrement default 0,
#		id integer not null default 0,
#		dte text,
#		price integer);"""
#	cursor.execute(cmd)
#
#	for state in pricedict.keys():
#		data = (state)
#		cmd = ("INSERT INTO prediction (state) VALUES " + str(data))
#		cursor.execute(cmd)
#		data = (pricedict[state])
#		for day in data.keys():
#			price = data[day]
#			data = (day, price)
#			cmd = ("INSERT INTO price (dte, price) VALUES " + str(data))
#			cursor.execute(cmd)

	


