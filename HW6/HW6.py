import sqlite3
from bs4 import BeautifulSoup
import urllib2

def get_elecvotes():
	"""
	makes a dictionary of states with respective electoral votes
	"""
	response = urllib2.urlopen("http://www.fec.gov/pages/elecvote.htm")
	html = response.read()
	response.close()

	page = BeautifulSoup(html)
	evdict = {}

	for tablerow in [x.findAll("td") for x in page.find('table').find_all('tr')[1:]]:
		datalist = [val.get_text() for val in tablerow]

		try: #because html table has weird blank entries
			state = str(datalist[0])
			votes = float(datalist[-1])
			evdict[state] = votes
		except:
			continue
	return evdict


#answer hw
def answer_hw():
	
	print "-"*50
	print "question a - create table called 'election' and populate it with statename, electoral votes, and intrade contract id"
	#get data
	evdict = get_elecvotes()

	#make table
	connection = sqlite3.connect("/Users/matar/Documents/Courses/PythonClass/HW6/tmp.db")
	cursor = connection.cursor()
	#define columns
	cmd = """CREATE TABLE election (
		id integer primary key autoincrement default 0,
		state text,
		electoral integer
		);"""
	cursor.execute(cmd)

	for state in evdict.keys():
		data = (state, evdict[state])
		cmd = ("INSERT INTO election (state,electoral) VALUES " + str(data))
		cursor.execute(cmd)

	#cursor.execute("DROP TABLE election")

	print 