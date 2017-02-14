import sys
import urllib3
from urllib3 import ProxyManager
import time
from bs4 import BeautifulSoup as BS

urllib3.disable_warnings()

class Downloader:	
	def __init__(self, proxyList):
		self.__proxyCounter = 0
		self.__proxyList = proxyList
		self.__http = ProxyManager("http://"+self.__proxyList[self.__proxyCounter])
		reload(sys)
		sys.setdefaultencoding('utf-8')
		
		
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
	
	def downloadToFile(self, url, fileAdress, tries=0):
		print "Start downloading from: '%s'" % (url)
		r = self.tryDownload(url)
		if r.status == 200:
			print "Downloaded. Saving to '%s'" % (fileAdress)
			f = open(fileAdress, 'w')
			f.write(r.data)
			f.close()
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

proxyList = [
	"95.31.29.209:3128",
	"77.50.220.92:8080",
	"91.217.42.2:8080",
	"62.122.100.90:8080",
	"62.165.42.170:8080",
	"83.169.202.2:3128",
	"82.146.52.210:8118"
]

dwnld = Downloader(proxyList)

class MacDownloader:
	siteName = "mcdonalds.ru"
	folder = "macdata"
	
	def downloadMain(self):
		url = "http://"+self.siteName+"/products"
		fileAdress = self.folder+"/main.html"
		dwnld.downloadToFile(url, fileAdress)
	
	def downloadPrices(self, arr):
		for key in arr.keys():
			for link in arr.get(key):
				url = "http://%s%s" % (self.siteName, link[1])
				fileAdress = self.folder+link[1]+".html"
				if dwnld.downloadToFile(url, fileAdress) == -1:
					print "Aborting..."
					sys.exit()
				time.sleep(1)

class KfcDownloader:
	siteName = "www.kfc.ru"
	folderName = "kfcdata"
