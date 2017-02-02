# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views import View

from models import ProductGroup, Product

import math
from random import randint
from random import random

import logging
log = logging.getLogger('django')
def findDesp(group):
	products = Product.objects.filter(group=group)
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

class Order:
	
	def __init__(self, summ):
		self.summ = float(summ)
		self.products=[]
		self.groups = []
		self.productsPriority = []
		self.setAverSum()
		self.setHowMany()
		self.amountOfMoney()
	
	def setAverSum(self):
		self.averSum = 0
		prodCount=0
		for group in ProductGroup.objects.all():
			if group.group_name == "Соусы":
				continue
			groupLen = len(Product.objects.filter(group=group))
			self.averSum+=group.average_price*groupLen
			prodCount += groupLen
		self.averSum /= prodCount
	
	def setHowMany(self):
		if self.averSum == None:
			return
		self.count = math.ceil(self.summ/self.averSum)
	
	def amountOfMoney(self):
		if self.count<3:
			self.money = 'l'
		elif self.count<7:
			self.money = 'm'
		else:
			self.money = 'h'
	
	def getRangeForMoney(self, group, size):
		gp = Product.objects.filter(group=group, price__gte=0)
		if size == 1:
			bot = gp.order_by('price')[0].price
			top = group.average_price
		if size == 2:
			bot = group.average_price-findDesp(group)*2/3
			top = group.average_price+findDesp(group)*2/3
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
		size = 1 if self.money=='l' else 2 if self.money == 'm' else 3
		size = 3
		range = self.getRangeForMoney(group, size)
		if range == -1:
			return -1
		products = Product.objects.filter(group=group, price__gte=range[0]).filter(price__lte=range[1])
		if len(products) == 1:
			log.info("[0] %s (%d %d)"%(products[0],range[0],range[1]))
			return products[0]
		elif len(products)==0:
			return -1
		else:
			prod = products[randint(0, len(products)-1)]
			log.info("%s (%d %d)"%(prod,range[0],range[1]))
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
			self.groups.append(group.group_name)
			self.productsPriority.append(priority)
			
	def compileOrder(self, size):
		for i in range(0, size):
			self.addProduct()


# Create your views here.
class DevView(View):
	def get(self, request, sum):
		l1 = Product.objects.filter(group=ProductGroup.objects.get(group_name="Напитки")).order_by('price')
		
		ord = Order(sum)
		ord.compileOrder(10)
		products=ord.products
		return render(request, 'macprice/index.html', { 'l1':l1, 'prodList':products, 'var':ord.count })

	
		
