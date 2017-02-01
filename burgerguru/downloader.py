import time
import urllib3
from bs4 import BeautifulSoup as BS

#supress warnings...
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#-------------------

def tryDownload(http, URL):
	try:
		r = http.request('GET', URL)
		return r;
	except:
		print "Proxy Error, trying again in 3 secs..."
		time.sleep(3)
		return tryDownload(http, URL)

siteName = 'http://mcdonalds.ru'

f = open('updater/pretty.html', 'r')
soup = BS(f.read(), 'html5lib')
f.close()

http = urllib3.ProxyManager('http://95.31.29.209:3128')

#hardParcing
products = soup.find('div', {'class':'products__list'})
prodDict = {}
rowList = products.findChildren('div', {'class':'row'})
for row in rowList:
	prodLinks = row.findChildren('a', {'class': 'products__item-link'})
	for a in prodLinks:
		URL = siteName+a['href'].strip()
		print "Downloading from: "+URL
		r = tryDownload(http, URL)
		if r.status == 200:
			print "Parsing..."
			priceSoup = BS(r.data, 'html5lib')
			print "Writing to file: \'updater"+a['href'].strip()+"\'";
			f = open('updater'+a['href'].strip()+".html", 'w')
			f.write(priceSoup.prettify().encode('utf-8', 'ignore'))
			f.close()
			print "Sucsess!"
		else:
			print "Wrong response status: "+str(r.status)
		time.sleep(1)

