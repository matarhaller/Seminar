import argparse
import urllib2
from xml.etree import ElementTree as etree
import operator
import math

def calculate(inputstr):
	"""Write a module called 'CalCalc' with a method 'calculate'
	that evaluates any string passed to it, 
	and can be used from either the command line (using argparse with reasonable flags) 
	or imported within Python. 
	
	EXAMPLE:
	$ python CalCalc.py -s '34*28'
	$  952
	---- AND, from within Python ----
	>>> from CalCalc import calculate
	>>> calculate('34*20')
	>>> 952
	"""
	try:
		ans = eval(inputstr, {'__builtins__':{}}, vars(math))
	except:
		ans = runwolfram(inputstr)
	return ans
	
def runwolfram(inputstr):
	url = makeurl(inputstr)
	site = urllib2.urlopen(url)
	s = site.read()
	site.close()	
	stree = etree.fromstring(s)

	xmldict = dict()
	for x in stree.findall('pod'):
		for y in x.findall('subpod'):
			for z in y.findall('plaintext'):
 				xmldict.update({x.get('id') : z.text})
	try:
		ans = xmldict['Result']
	except:
		ans = "Wolfram Alpha doesn't know the answer. Please try a different question"
	return ans

def makeurl(inputstr):
	inputstr = inputstr.split()
	parsedlist = [urllib2.quote(s.encode("utf8")) for s in inputstr]
	parsedlist = [s+'+' for s in parsedlist]
	finalinput = ''.join(parsedlist)
	url = 'http://api.wolframalpha.com/v2/query?input=' + finalinput + '&appid=UAGAWR-3X6Y8W777Q'
	return url

def test_1():
	assert abs(4. - calculate('2**2')) < .001
	
def test_2():
	assert calculate("what was the unix time of elvis's birth?") == '-1103904000 (Unix time)'


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "CalCalc from command line")
	parser.add_argument('-s', action = 'store', dest = 'inputstr', help = "input string to query")	
	args = parser.parse_args()
	print calculate(args.inputstr)