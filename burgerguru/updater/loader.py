import urllib3
from urllib3 import ProxyManager
import time
from bs4 import BeautifulSoup as BS

urllib3.disable_warnings()

class Downloader:
	siteName = 'mcdonalds.ru'
	folder = "updaterdata"
	
	def __init__(self, proxyList):
		self.__proxyCounter = 0
		self.__proxyList = proxyList
		self.__http = ProxyManager("http://"+self.__proxyList[self.__proxyCounter])
		
		
		
	def tryDownload(self, url, tries=0):
		try:
			r = self.__http.request('GET', url)
		except:
			if tries>2:
				print "To many tries, updating proxy..."
				self.updateProxy()
				r = self.tryDownload(url)
			else:
				print "Error while downloading from \'%s\'. Trying again in 3 secs... [%d]" % (url, tries+1) 
				time.sleep(3)
				r = self.tryDownload(url, tries+1)
		return r
	
	def updateProxy(self):
		self.__proxyCounter += 1
		if self.__proxyCounter >= len(proxyList):
			self.__proxyCounter = 0
		self.__http = ProxyManager("http://"+self.__proxyList[self.__proxyCounter])
	
	def downloadParseToFile(self, url, fileAdress, tries=0):
		print "Start downloading from: '%s'" % (url)
		r = self.tryDownload(url)
		if r.status == 200:
			print "Downloaded. Parsing and saving to '%s'" % (fileAdress)
			soup = BS(r.data, 'html5lib')
			f = open(fileAdress, 'w')
			f.write(soup.prettify().encode('utf-8', 'ignore'))
			f.close()
			print "Sucsess!"
		elif r.status//100 == 5:
			print "Something wrong with server (%s). Waiting 2 secs and trying again... [%d]" % (r.status, tries+1)
			time.sleep(2)
			if tries<5:
				self.downloadParseToFile(url, fileAdress, tries+1)
			else:
				print "Too many tries. Aborting! Try to start update later"
				return -1
		else:
			print "Wrong response status: %d" % (r.status)
	
	def downloadMain(self):
		if self.downloadParseToFile("http://"+self.siteName+"/products", self.folder+'/main.html', 'w')==-1:
			print "Aborting..." #?!
			sys.exit()
	
	def downloadEachPrice(self, products):
		for key in products.keys():
			for link in products.get(key):
				url = "http://%s%s" % (self.siteName, link[1])
				fileAdress = self.folder+link[1]+".html"
				if self.downloadParseToFile(url, fileAdress) == -1:
					print "Aborting..."
					sys.exit()
				time.sleep(1)
