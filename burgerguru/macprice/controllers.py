# -*- coding: utf-8 -*-

from random import randint
from random import random
import math, numpy
from models import ProductGroup, Product, User, Resturant

types = {
			"N":u"",
			"S":u" (мал.)",
			"M":u" (станд.)",
			"L":u" (бол.)",
			"X":u" (оч.бол.)",
		}

def createOrder(summ, restName):
	responseText = ""
	prodCheckArray = []
	orderCounter = 0;
	attempts = 0
	for i in range(1, 4):
		ord = Order(summ, Resturant.objects.get(short_name=restName))
		ord.size = i
		ord.compileOrder(int(int(summ)*0.04))
		if ord.products in prodCheckArray:
			i -= 1
			attempts += 1
			if attempts > 6:
				break;
			continue;
		else:
			orderCounter+=1
			
		orderText = u"*Ваш заказ. Вариант№%d:*\n"%orderCounter
		counter=0
		priceSum = 0
		if restName == "mac": ccalSum = 0
		for prod in ord.products:
			counter+=1
			priceSum+=prod.price
			if restName == "mac": ccalSum += prod.ccal
			name = prod.product_name
			name+=types[prod.product_type]
			s = u"{0}){1}: {2}руб.{3}ккал.\n".format(counter, name, prod.price, prod.ccal) if restName == "mac" else u"{0}){1}: {2}руб.\n".format(counter, name, prod.price) 
			orderText+=s
		if restName == "mac": orderText += u"*Калорийность: %i ккал.*\n" % ccalSum
		orderText+=u"*Итого: %i руб.*"%priceSum
		responseText += orderText + "\n\n"
		prodCheckArray.append(ord.products)
		
	responseText+=u"Приятного аппетита!"
	return responseText;


class Order:
	def __init__(self, summ, resturant):
		self.size = 2
		self.products=[]
		self.groups = []
		self.prodNames = []
		self.productsPriority = []
		self.attempts = 0
		self.summ = float(summ)
		self.rest = resturant
	
	def getRangeForGroup(self, group, size):
		gp = [p.price for p in Product.objects.filter(group=group, price__gte=0, resturant=self.rest)]
		first = int(numpy.percentile(gp, 34))
		second = int(numpy.percentile(gp, 67))
		max = int(numpy.max(gp))
		min = int(numpy.min(gp))
		bot, top = (min, first-1) if size == 1 else (first, second-1) if size==2 else (second, max)
		return [bot, top, top-bot]
		
		
	def getRangeForMoney(self, group):
		bt = self.getRangeForGroup(group, self.size)
		bot = bt[0]
		top = bt[1]
		
		if self.summ>=top:
			return [bot, top]
		elif self.summ<bot:
			if self.size!=1:
				self.size+=-1
				return self.getRangeForMoney(group)
			else:
				return -1
		else:
			return [bot, self.summ]
	
	def getFromGroup(self, group):
		if self.summ<50:
			self.size=1
		
		priceRange = self.getRangeForMoney(group)
		if priceRange == -1:
			return -1
		products = Product.objects.filter(group=group, price__gte=priceRange[0], resturant=self.rest).filter(price__lte=priceRange[1])
		if len(products) == 1:
			return products[0]
		elif len(products)==0:
			return -1
		else:
			rnd = randint(0, len(products)-1)
			prod = products[rnd]
			
			for i in range(0, len(products)):
				if not prod.product_name in self.prodNames:
					break
				if rnd+i>=len(products):
					rnd+=-len(products)
				prod = products[rnd+i]
			
			return prod
	
	def getNewGroup(self, groups, rnd=-1, deepness=0):
		if rnd>=len(groups):
			rnd = 0
		offset = randint(0, len(groups)-1) if rnd == -1 else rnd
		grp = groups[offset]
		if grp.group_name in self.groups and deepness<len(groups):
			return self.getNewGroup(groups,offset+1,deepness+1)
		elif deepness<len(groups):
			return grp
		else:
			#all groups were used
			return groups[randint(0, len(groups)-1)]
	
	def addProduct(self):
		if len(self.productsPriority)<3:
			priority = len(self.productsPriority)+1
		else:
			priority = 1 if random()>0.6 else 3
		
		groups = ProductGroup.objects.filter(priority = priority, resturant=self.rest)
		group = self.getNewGroup(groups)
		prod = self.getFromGroup(group)
			
		if prod != -1 and prod.product_name not in self.prodNames:
			self.summ+= -prod.price
			self.products.append(prod)
			self.prodNames.append(prod.product_name)
			self.groups.append(group.group_name)
			self.productsPriority.append(priority)
			return 0
		else:
			if self.attempts>10:
				return 0
			else:
				self.attempts+=1
				return -1
			
	def compileOrder(self, size):
		for i in range(0, size):
			i+=self.addProduct()
		
		if self.summ>=19:
			sousi = Product.objects.filter(group = ProductGroup.objects.filter(priority=9, resturant=self.rest)[0], resturant=self.rest)
			nap = Product.objects.filter(group = ProductGroup.objects.filter(priority=2, resturant=self.rest)[0], resturant=self.rest)
			for prod in self.products:
				if prod.product_type != "N":
					if len(Product.objects.filter(product_name=prod.product_name, resturant=self.rest)) == 3 and not prod in nap:
						self.products.append(sousi[randint(0, len(sousi)-1)])
						self.summ += -sousi[0].price
						if self.summ<19:
							break

def createDictResturants():
	diction = {}
	for part in User.RESTURANT_CHOICES:
		diction[part[1]] = part[0]
	return diction
