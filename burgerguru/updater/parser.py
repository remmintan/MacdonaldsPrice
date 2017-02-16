# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS

import sys

import os
os.environ["DJANGO_SETTINGS_MODULE"]="burgerguru.settings"

import django
django.setup()

from macprice.models import Product, ProductGroup, Resturant

def createSoupFromFile(fileAdress):
	print "Parsing file: %s" % fileAdress
	f = open(fileAdress, 'r')
	data = f.read()
	soup = BS(data, 'html5lib')
	return soup

class MacParser:
	rest = "mac"
	folder = "macdata"
	products = {}
	
	def parseMain(self):
		soup = createSoupFromFile(self.folder+'/main.html')
		products = soup.find('div', {'class':'products__list'})
		rowList = products.findChildren('div', {'class':'row'})
		for row in rowList:
			catTitle = row.findChildren('h2', {'class':'products__cat-title'})[0]
			prodLinks = row.findChildren('a', {'class': 'products__item-link'})
			self.products[catTitle.text.strip()] = []
			for a in prodLinks:
				self.products[catTitle.text.strip()].append( [a['title'].strip(), a['href'].strip()] )
		print "Sucsess!"
		
	def parsePrices(self):
		for key in self.products.keys():
			newArray = []
			for link in self.products.get(key):
				fileAdress = self.folder+link[1]+".html"
				soup = createSoupFromFile(fileAdress)
				prices = self.getPrices(soup)
				ccals = self.getCcals(soup)
				newArray.append([link[0], prices[0], prices[1], ccals])
			self.products[key] = newArray
		
		print "Start govnocode section:"
		deserts = []
		for spec in self.products.get(u'Десерты'):
			if u'Молочный' in spec[0]:
				deserts.append(spec)
				
		for spec in deserts:
			self.products.get(u'Десерты').remove(spec)
			self.products.get(u'Напитки').append(spec)
		
	def getPrices(self, soup):
		priceList = soup.find_all('h4', {'class':'product__show-price'});
		prodType = "singular" if len(priceList) == 1 else "plural"
		priceArr = []
		for p in priceList:
			priceText = p.text.strip().split(' ')[0]
			if priceText == "":
				priceArr.append(-1)
			else:
				priceArr.append(int(priceText))
					
		return (priceArr, prodType)
	
	def getCcals(self, soup):
		tabsContent = soup.find_all('div', {'class':'product__show-composition'})[0].findChildren('div', {'class': 'tabs__content'})[0]
		ccalList = tabsContent.findChildren('div', {'class': 'tab'})
		ccalArr = []
		for ccal in ccalList:
			text = ccal.findChildren('tr')[2].findChildren('span')[0].text.strip()
			if text == "":
				ccalArr.append(0)
			else:
				ccalArr.append(int(float(text)))
		return ccalArr
	
	#DJANGO STUFF below
	
	def updateDjango(self):
		self.__resturan = Resturant.objects.get(short_name=self.rest)
		
		for key in self.products.keys():
			if ProductGroup.objects.filter(group_name=key, resturant=self.__resturan).exists():
				pg = ProductGroup.objects.filter(group_name=key, resturant=self.__resturan)[0]
				print "Updating group: %s" % (pg)
			else:
				pg = ProductGroup(group_name = key, resturant=self.__resturan)
				pg.save()
				print "Creating group: %s" % (pg)
			
			prodArr = self.products.get(key)
			priceSum = 0
			withoutSum = 0
			count = 0
			for prod in prodArr:
				print "Updating %s product %s" % (prod[2], prod[0])
				if prod[2] == "singular":
					if Product.objects.filter(product_name = prod[0], group = pg).exists():
						p = Product.objects.filter(product_name = prod[0], group = pg)[0]
						p.update(prod[1][0], self.rest, prod[3][0])
					else:
						p = Product(product_name=prod[0], group = pg, price=prod[1][0], resturant=self.__resturan, ccal = prod[3][0])
						p.save()
					
					if prod[1][0] != -1:
						priceSum += prod[1][0]
						count+=1
					else:
						withoutSum+=1
				else:
					#govnokod
					self.updatePlural(pg, "S", 0, prod)
					if len(prod[1])>1:
						self.updatePlural(pg, "M", 1, prod)
					if len(prod[1])>2:
						self.updatePlural(pg, "L", 2, prod)
					if len(prod[1])>3:
						self.updatePlural(pg, "X", 3, prod)
						
					
					if prod[1][0]!=-1:
						priceSum += prod[1][0]
						count+=1
						if len(prod[1])>1:
							priceSum += prod[1][1]
							count+=1
						if len(prod[1])>2:
							priceSum += prod[1][2]
							count+=1
					else:
						withoutSum+=len(prod[1])
			
			pg.average_price = priceSum/(count-withoutSum)
			#print "%s		priceSum:%d  prodArr:%d  withoutSum:%d  average:%d" % (pg, priceSum, count, withoutSum, pg.average_price)
			pg.save()
			print "Sucsess!"
			
		self.mirrorCheck()
	
	def mirrorCheck(self):
		print "Starting mirror check..."
		keysArr = self.products.keys()
		for group in ProductGroup.objects.filter(resturant=self.__resturan):
			if group.group_name not in keysArr:
				print "Deleting redundant group: %s" %(group.group_name)
				group.delete()
				continue;
			prodArr = [prod[0] for prod in self.products.get(group.group_name)]
			for product in Product.objects.filter(group = group):
				if product.product_name not in prodArr:
					print "Deleting redundant object: %s" % (product.product_name)
					product.delete()
				
	
	def updatePlural(self, pg, pType, i, prod):
		if Product.objects.filter(product_name = prod[0], group = pg, product_type=pType).exists():
			p = Product.objects.filter(product_name = prod[0], group = pg, product_type=pType)[0]
			p.update(prod[1][i], self.rest, prod[3][i])
		else:
			p = Product(product_name=prod[0], group = pg, price=prod[1][i], product_type=pType, resturant = Resturant.objects.filter(short_name=self.rest)[0], ccal = prod[3][i])
			p.save()
	
	def setPriority(self, arr):
		reload(sys)
		sys.setdefaultencoding('utf-8')
		self.__resturan = Resturant.objects.get(short_name=self.rest)
		groups = ProductGroup.objects.filter(resturant=self.__resturan);
		for grp in groups:
			print "Setting up priority for: %s" % grp.group_name
			if grp.group_name in arr.keys():
				grp.priority = arr[grp.group_name]
				grp.save()
			else:
				print "Can't find"
class KfcParser:
	rest = "kfc"
	folder = "kfcdata"
	products = {}
	
	def parseMain(self):
		soup = createSoupFromFile(self.folder+"/main.html")
		menu = soup.find('li', {'class': 'menu'})
		ul = menu.findChild('ul', {'class':'sub-nav'})
		self.cats = [a['href'] for a in ul.findChildren('a')]
	
	def parseCats(self):
		for cat in self.cats:
			fileAdress = self.folder+cat+".html"
			soup = createSoupFromFile(fileAdress)
			h1 = soup.find('h1', {'class':'page-title'})
			if h1 is None:
				break
			catName = h1.text.strip()
			self.products[catName] = []
			
			prods = soup.findChild('ul', {'class':'products-detail-list group'})
			lis = prods.findChildren('li')
			for li in lis:
				url = li.findChild('a')['href']
				name = li.findChild('h4').text
				self.products[catName].append([name, url])
	
	def parsePrices(self):
		for key in self.products.keys():
			newArr = []
			for val in self.products.get(key):
				fa = self.folder+val[1]+".html"
				soup = createSoupFromFile(fa)
				price = soup.find('h3', {'class':'price'}).text.strip().split()[0]
				newArr.append([val[0], int(price)])
			self.products[key] = newArr

	#DJANGO stuff below
	def updateDjango(self):
		self.__resturan = Resturant.objects.get(short_name=self.rest)
		for key in self.products.keys():
			if ProductGroup.objects.filter(group_name=key, resturant=self.__resturan).exists():
				pg = ProductGroup.objects.filter(group_name=key, resturant=self.__resturan)[0]
				print "Updating group: %s" % (pg)
			else:
				pg = ProductGroup(group_name = key, resturant=self.__resturan)
				pg.save()
				print "Creating group: %s" % (pg)
			prodArr = self.products.get(key)
			priceSum = 0
			withoutSum = 0
			count = 0
			for prod in prodArr:
				if Product.objects.filter(product_name = prod[0], group = pg).exists():
					p = Product.objects.filter(product_name = prod[0], group = pg)[0]
					p.update(prod[1], self.rest, 0)
				else:
					p = Product(product_name=prod[0], group = pg, price=prod[1], resturant=self.__resturan, ccal = 0)
					p.save()
				priceSum += p.price
				count += 1
			pg.average_price = int(float(priceSum)/float(count))
			pg.save()

	def setPriority(self, arr):
		reload(sys)
		sys.setdefaultencoding('utf-8')
		self.__resturan = Resturant.objects.get(short_name=self.rest)
		groups = ProductGroup.objects.filter(resturant=self.__resturan);
		for grp in groups:
			print "Setting up priority for: %s" % grp.group_name
			if grp.group_name in arr.keys():
				grp.priority = arr[grp.group_name]
				grp.save()
			else:
				print "Can't find"
