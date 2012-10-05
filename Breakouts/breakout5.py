import urllib2
from bs4 import BeautifulSoup

response = urllib2.urlopen("http://www.realclearpolitics.com/epolls/2012/president/fl/florida_romney_vs_obama-1883.html#polls")
html = response.read()
response.close

soup = BeautifulSoup(html)
initial = soup.find(id = "polling-data-full").findAll("tr") #table rows - first row is header row

