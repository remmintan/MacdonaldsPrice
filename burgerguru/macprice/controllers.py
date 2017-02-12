# -*- coding: utf-8 -*-

from random import randint
from random import random
import math
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
	for i in range(1, 4):
		ord = Order(summ, Resturant.objects.filter(short_name=restName)[0])
		ord.size = i
		ord.compileOrder(int(int(summ)*0.04))
		orderText = u"*Ваш заказ. Вариант№%d:*\n"%i
		counter=0
		priceSum = 0
		ccalSum = 0
		for prod in ord.products:
			counter+=1
			priceSum+=prod.price
			ccalSum += prod.ccal
			name = prod.product_name
			name+=types[prod.product_type]
			s = u"{0}){1}: {2}руб.{3}ккал.\n".format(counter, name, prod.price, prod.ccal)
			orderText+=s
		orderText += u"*Калорийность: %i ккал.*\n" % ccalSum
		orderText+=u"*Итого: %i руб.*"%priceSum
		responseText += orderText + "\n\n"
		
	responseText+=u"Приятного аппетита!"
	return responseText;


class Order:
	def __init__(self, summ, resturant):
		self.summ = float(summ)
		self.products=[]
		self.groups = []
		self.prodNames = []
		self.productsPriority = []
		self.rest = resturant
		self.setAverSum()
		self.setHowMany()
		self.size = 2
		
	
	def setAverSum(self):
		self.averSum = 0
		prodCount=0
		for group in ProductGroup.objects.all():
			if group.group_name == u"Соусы":
				continue
			groupLen = len(Product.objects.filter(group=group, resturant=self.rest))
			self.averSum+=group.average_price*groupLen
			prodCount += groupLen
		self.averSum /= prodCount
	
	def setHowMany(self):
		if self.averSum == None:
			return
		self.count = math.ceil(self.summ/self.averSum)
	
	def getRangeForMoney(self, group, size):
		gp = Product.objects.filter(group=group, price__gte=0, resturant=self.rest).order_by('-price')
		if size == 1:
			bot = gp.order_by('price')[0].price
			top = group.average_price
		if size == 2:
			bot = group.average_price-self.findDesp(group)/2
			top = group.average_price+self.findDesp(group)/2
		if size == 3:
			bot = group.average_price
			top = gp.order_by('-price')[0].price
		
		if self.summ>=top:
			return [bot, top]
		elif self.summ<bot:
			if size!=1:
				return self.getRangeForMoney(group, size-1)
			else:
				return -1
		else:
			return [bot, self.summ]
	
	def getFromGroup(self, group):
		size = self.size
		
		if self.summ<50:
			size=1
		
		priceRange = self.getRangeForMoney(group, size)
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
			priority = 1 if random()>0.7 else 3
		
		groups = ProductGroup.objects.filter(priority = priority)
		group = self.getNewGroup(groups)
		prod = self.getFromGroup(group)
			
		if prod != -1:
			self.summ+= -prod.price
			self.products.append(prod)
			self.prodNames.append(prod.product_name)
			self.groups.append(group.group_name)
			self.productsPriority.append(priority)
			
	def compileOrder(self, size):
		for i in range(0, size):
			self.addProduct()
		
		if self.summ>=19:
			sousi = Product.objects.filter(group = ProductGroup.objects.filter(priority=9)[0], resturant=self.rest)
			nap = Product.objects.filter(group = ProductGroup.objects.filter(priority=2)[0], resturant=self.rest)
			for prod in self.products:
				if prod.product_type != "N":
					if len(Product.objects.filter(product_name=prod.product_name, resturant=self.rest)) == 3 and not prod in nap:
						self.products.append(sousi[randint(0, len(sousi)-1)])
						self.summ += -sousi[0].price
						if self.summ<19:
							break
							
	def findDesp(self, group):
		products = Product.objects.filter(group=group, resturant=self.rest)
		summ = 0
		colProds = len(products)
		for product in products:
			if product.price == -1:
				colProds+=-1
			else:
				summ += (product.price - group.average_price)**2
		summ /= colProds
		summ = math.sqrt(summ)
		
		return summ

def createDictResturants():
	diction = {}
	for part in User.RESTURANT_CHOICES:
		diction[part[1]] = part[0]
	return diction
