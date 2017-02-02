# -*- coding:utf-8 -*-

import urllib3
from urllib3 import ProxyManager
import time
from bs4 import BeautifulSoup as BS
import sys
from decimal import Decimal

import os
os.environ["DJANGO_SETTINGS_MODULE"]="burgerguru.settings"

import django
django.setup()

from macprice.models import Product, ProductGroup

MAIN_FOLDER = "updater"
MAIN_FILE = "main.html"

PRODUCTS_DICTIONARY = {}

urllib3.disable_warnings()

class Downloader:
	siteName = 'mcdonalds.ru'
	
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
				r = tryDownload(url)
			else:
				print "Error while downloading from \'%s\'. Trying again in 3 secs... [%d]" % (url, tries+1) 
				time.sleep(3)
				r = self.tryDownload(url, tries+1)
		return r
	
	def updateProxy(self):
		self.__proxyCounter += 1
		if self.__proxyCounter >= len(proxyList):
			self.__proxyCounter = 0
		self.__http = ProxyManager(self.__proxyList[self.__proxyCounter])
	
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
		if self.downloadParseToFile("http://"+self.siteName+"/products", MAIN_FOLDER+'/'+MAIN_FILE, 'w')==-1:
			print "Aborting..."
			sys.exit()
		
	
	def downloadEachPrice(self):
		for key in PRODUCTS_DICTIONARY.keys():
			for link in PRODUCTS_DICTIONARY.get(key):
				url = "http://%s%s" % (self.siteName, link[1])
				fileAdress = MAIN_FOLDER+link[1]+".html"
				if self.downloadParseToFile(url, fileAdress) == -1:
					print "Aborting..."
					sys.exit()
				time.sleep(1)

class Updater:
	def parseMain(self):
		print "Parsing main file into products dictionary..."
		f = open(MAIN_FOLDER+'/'+MAIN_FILE, 'r')
		data = f.read()
		soup = BS(data, 'html5lib')
		products = soup.find('div', {'class':'products__list'})
		rowList = products.findChildren('div', {'class':'row'})
		for row in rowList:
			catTitle = row.findChildren('h2', {'class':'products__cat-title'})[0]
			prodLinks = row.findChildren('a', {'class': 'products__item-link'})
			PRODUCTS_DICTIONARY[catTitle.text.strip()] = []
			for a in prodLinks:
				PRODUCTS_DICTIONARY[catTitle.text.strip()].append( [a['title'].strip(), a['href'].strip()] )
		print "Sucsess!"
		
	def parsePrices(self):
		for key in PRODUCTS_DICTIONARY.keys():
			newArray = []
			for link in PRODUCTS_DICTIONARY.get(key):
				fileAdress = MAIN_FOLDER+link[1]+".html"
				print("Start parsing for: '%s'") % (fileAdress)
				f = open(fileAdress, 'r')
				soup = BS(f.read(), 'html5lib')
				f.close()
				priceList = soup.find_all('h4', {'class':'product__show-price'});
				prodType = "singular"
				if len(priceList) == 1:
					p = priceList[0].text.strip().split(' ')[0]
					if p == "":
						price = [-1]
					else:
						price = [int(p)]
				elif len(priceList) == 0:
					price = [-1]
				else:
					price = []
					prodType = "plural"
					for p in priceList:
						priceText = p.text.strip().split(' ')[0]
						if priceText == "":
							price. append(-1)
						else:
							price.append(int(priceText))
				newArray.append([link[0], price, prodType])
				print "Sucsess! Sleep 1 sec"
				#uncomment before deploying!
				#time.sleep(1)
			PRODUCTS_DICTIONARY[key] = newArray
	
	def mirrorCheck(self):
		print "Starting mirror check..."
		keysArr = PRODUCTS_DICTIONARY.keys()
		for group in ProductGroup.objects.all():
			if group.group_name not in keysArr:
				print "Deleting redundant group: %s" %(group.group_name)
				group.delete()
				continue;
			prodArr = [prod[0] for prod in PRODUCTS_DICTIONARY.get(group.group_name)]
			for product in Product.objects.filter(group = group):
				if product.product_name not in prodArr:
					print "Deleting redundant object: %s" % (product.product_name)
					product.delete()
				
	
	def updatePlural(self, pg, pType, i, prod):
		if Product.objects.filter(product_name = prod[0], group = pg, product_type=pType).exists():
			p = Product.objects.filter(product_name = prod[0], group = pg, product_type=pType)[0]
			p.update(prod[1][i])
		else:
			p = Product(product_name=prod[0], group = pg, price=prod[1][i], product_type=pType)
			p.save()
	
	def updateDjango(self):
		for key in PRODUCTS_DICTIONARY.keys():
			if ProductGroup.objects.filter(group_name=key).exists():
				pg = ProductGroup.objects.filter(group_name=key)[0]
				print "Updating group: %s" % (pg)
			else:
				pg = ProductGroup(group_name = key)
				pg.save()
				print "Creating group: %s" % (pg)
			
			prodArr = PRODUCTS_DICTIONARY.get(key)
			priceSum = 0
			withoutSum = 0
			for prod in prodArr:
				print "Updating %s product %s" % (prod[2], prod[0])
				if prod[2] == "singular":
					if Product.objects.filter(product_name = prod[0], group = pg).exists():
						p = Product.objects.filter(product_name = prod[0], group = pg)[0]
						p.update(prod[1][0])
					else:
						p = Product(product_name=prod[0], group = pg, price=prod[1][0])
						p.save()
					
					if prod[1][0] != -1:
						priceSum += prod[1][0]
					else:
						withoutSum+=1
				else:
					#govnokod
					self.updatePlural(pg, "S", 0, prod)
					if len(prod[1])>1:
						self.updatePlural(pg, "M", 1, prod)
					if len(prod[1])>2:
						self.updatePlural(pg, "L", 2, prod)
					
					if prod[1][0]!=-1:
						priceSum += prod[1][0]
						if len(prod[1])>1:
							priceSum += prod[1][1]
						if len(prod[1])>2:
							priceSum += prod[1][2]
					else:
						withoutSum+=len(prod[1])
			
			pg.average_price = Decimal(float(priceSum)/float(len(prodArr)-withoutSum))
			pg.save()
			print "Sucsess!"
			
		self.mirrorCheck()
	
	def setPrioty(self, priorDict):
		for key in priorDict.keys():
			try:
				print "Setting up priority for: %s" % (key)
				group = ProductGroup.objects.get(group_name=key)
				group.priority = priorDict.get(key)
				group.save()
			except ProductGroup.DoesNotExist:
				print "For some reason can't find group for: %s" % key
			

proxyList = [
	"95.31.29.209:3128",
	"77.50.220.92:8080",
	"91.217.42.2:8080",
	"62.122.100.90:8080",
	"62.165.42.170:8080",
	"83.169.202.2:3128",
	"82.146.52.210:8118"
]
import sys

dwnld = Downloader(proxyList)
upd = Updater()
if "-load" in sys.argv:
	dwnld.downloadMain()
if "-upd" in sys.argv:
	upd.parseMain()
if "-load" in sys.argv:
	dwnld.downloadEachPrice()
if "-upd" in sys.argv:
	upd.parsePrices()
if "-upd" in sys.argv:
	upd.updateDjango()

priorDict = {
	"Сандвичи":1,
	"Напитки": 2,
	"Кофе, чай": 2,
	"Картофель": 3,
	"Десерты":3,
	"Салаты":3,
	"Соусы":4
}
if "-prior" in sys.argv:
	upd.setPrioty(priorDict)
