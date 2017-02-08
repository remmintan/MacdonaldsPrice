# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS

import os
os.environ["DJANGO_SETTINGS_MODULE"]="burgerguru.settings"

import django
django.setup()

from macprice.models import Product, ProductGroup, Resturant

class Updater:
	folder = "updaterdata"
	curRest = "mac"
	
	def __init__(self):
		self.products = {}
	
	def parseMain(self, curRest):
		self.curRest = curRest
		
		print "Parsing main file into products dictionary..."
		f = open(self.folder+'/main.html', 'r')
		data = f.read()
		soup = BS(data, 'html5lib')
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
			self.products[key] = newArray
		
		print "Start govnocode section:"
		deserts = []
		for spec in self.products.get(u'Десерты'):
			if u'Молочный' in spec[0]:
				deserts.append(spec)
				
		for spec in deserts:
			self.products.get(u'Десерты').remove(spec)
			self.products.get(u'Напитки').append(spec)
		
	
	def mirrorCheck(self):
		print "Starting mirror check..."
		keysArr = self.products.keys()
		for group in ProductGroup.objects.all():
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
			p.update(prod[1][i], self.curRest)
		else:
			p = Product(product_name=prod[0], group = pg, price=prod[1][i], product_type=pType, resturant = Resturant.objects.filter(short_name=self.curRest)[0])
			p.save()
	
	def updateDjango(self):
		for key in self.products.keys():
			if ProductGroup.objects.filter(group_name=key).exists():
				pg = ProductGroup.objects.filter(group_name=key)[0]
				print "Updating group: %s" % (pg)
			else:
				pg = ProductGroup(group_name = key)
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
						p.update(prod[1][0], self.curRest)
					else:
						p = Product(product_name=prod[0], group = pg, price=prod[1][0], resturant = Resturant.objects.filter(short_name=self.curRest)[0])
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
			print "%s		priceSum:%d  prodArr:%d  withoutSum:%d  average:%d" % (pg, priceSum, count, withoutSum, pg.average_price)
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
