""" Write a module called ‘CalCalc’, with a method called ‘calculate’ that evaluates any string passed to it, and can be used from either the command line (using argparse with reasonable flags) or imported within Python. Feel free to use something like eval(), but be aware of some of the nasty things it can do, and make sure it doesn’t have too much power: http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
EXAMPLE:
$ python CalCalc.py -s '34*28'
$  952
---- AND, from within Python ----
>>> from CalCalc import calculate
>>> calculate('34*20')
>>> 952
"""
import argparse
import urllib2
from xml.etree import ElementTree as etree


def calculate(inputstr):
	"""Evaluates any string passed
	
	EX: calculate('34*90') returns 952"""
	
	inputstr = inputstr.split()
	parsedlist = [urllib2.quote(s.encode("utf8")) for s in inputstr]
	parsedlist = [s+'+' for s in parsedlist]
	finalinput = ''.join(parsedlist)
	url = 'http://api.wolframalpha.com/v2/query?input=' + finalinput + '&appid=UAGAWR-3X6Y8W777Q'
	
	site = urllib2.urlopen(url)
	s = site.read()
	site.close()	
	
	stree = etree.fromstring(s)
	xmldict = dict()
	for x in stree.findall('pod'):
		for y in x.findall('subpod'):
			for z in y.findall('plaintext'):
			 	xmldict.update({x.get('title') : z.text})
	
	

if name == "__main__":
	parser = argparse.ArgumentParser(description = "CalCalc from command line")
	parser.add_argument('-s', action = 'store', dest = 'inputstring', help = "input string to query")
	
	args = parser.parse_args()
	
	ans = calculate(args)
	
	return ans