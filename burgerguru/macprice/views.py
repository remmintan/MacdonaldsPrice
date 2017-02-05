# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
		self.prodNames = []
		self.productsPriority = []
		self.setAverSum()
		self.setHowMany()
		self.size = 2
	
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
	
	def getRangeForMoney(self, group, size):
		gp = Product.objects.filter(group=group, price__gte=0).order_by('-price')
		if size == 1:
			bot = gp.order_by('price')[0].price
			top = group.average_price
		if size == 2:
			bot = group.average_price-findDesp(group)/2
			top = group.average_price+findDesp(group)/2
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
		products = Product.objects.filter(group=group, price__gte=priceRange[0]).filter(price__lte=priceRange[1])
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
			sousi = Product.objects.filter(group = ProductGroup.objects.filter(priority=9)[0])
			nap = Product.objects.filter(group = ProductGroup.objects.filter(priority=2)[0])
			for prod in self.products:
				if prod.product_type != "N":
					if len(Product.objects.filter(product_name=prod.product_name)) == 3 and not prod in nap:
						self.products.append(sousi[randint(0, len(sousi)-1)])
						self.summ += -sousi[0].price
						if self.summ<19:
							break


# Create your views here.
class DevView(View):
	def get(self, request, sum):
		l1 = Product.objects.filter(group=ProductGroup.objects.get(group_name="Кофе, чай")).order_by('price')
		
		iterations = int(int(sum)*0.04)
		var = []
		
		ord = Order(sum)
		ord.size = 1
		ord.compileOrder(iterations)
		products1=ord.products
		var.append(int(sum)-int(ord.summ))
		
		ord = Order(sum)
		ord.size = 2
		ord.compileOrder(iterations)
		products2=ord.products
		var.append(int(sum)-int(ord.summ))
		
		ord = Order(sum)
		ord.size = 3
		ord.compileOrder(iterations)
		products3=ord.products
		var.append(int(sum)-int(ord.summ))
		
		return render(request, 'macprice/index.html', { 'l1':l1, 'prodList':products1, 'prodList2':products2, 'prodList3':products3, 'var':var})

import telepot
import json
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest

#MacPriceBot------------------------
def processInput(bot, message, error):
	summ = 0
	chat_id = message['chat']['id']
	text = message['text']
	arrText = text.split()
	try:
		for strr in arrText:
			int(float(strr))
	except:
		bot.sendMessage(chat_id, "Неверный ввод. Отправьте только сумму(в рублях), которую вы готовы потратить на заказ. Также попробуйте команду: /help")
		return
	if len(arrText)>1:
		bot.sendMessage(chat_id, "Вы ввели %d чисел, мне нужно только одно: сумма (в рублях) которую вы готовы потратить на заказ. Также попробуйте команду: /help" % len(arrText))
		return
	
	try:
		summ = int(float(text))
	except:
		bot.sendMessage(chat_id, error)
		return;
	
	#input is ok. Processing sum
	if summ>10000:
		bot.sendMessage(chat_id, "Сумму нужно указывать в Российских рублях. Кажется вы ошиблись. (Сумма снижена до 1000)")
	elif summ>5000:
		bot.sendMessage(chat_id, "Вау! Сколько денег! Может быть посоветовать вам ближайший ресторан? (Сумма снижена до 1000)")
		summ = 1000
	elif summ>1000:
		bot.sendMessage(chat_id, "1000 рублей более чем достаточно, что бы наесться в макдоналдсе. (Сумма снижена до 1000)")
	
	if summ>1000:
		summ = 1000
	
	responseText = ""
	
	for i in range(1, 4):
		ord = Order(summ)
		ord.size = i
		ord.compileOrder(int(int(summ)*0.04))
		orderText = "Ваш заказ. Вариант№%d:\n"%i
		counter=0
		sum = 0
		for prod in ord.products:
			counter+=1
			sum+=prod.price
			name = prod.product_name
			
			if prod.product_type == 'S':
				name+=' (мал.)'
			elif prod.product_type == 'M':
				name+=' (станд.)'
			elif prod.product_type == 'L':
				name+=' (бол.)'
			s = ("{0}){1} - {2} руб.\n".format(counter, name, prod.price)).encode('utf-8')
			orderText+=s
		orderText+="Итого: %d"%sum
		responseText += orderText + "\n\n"
		
	responseText+="Приятного аппетита!"
	bot.sendMessage(chat_id, responseText)

commands = {
		"start":"Введите сумму (в рублях), которую вы готовы потратить и я подскажу вам несколько заказов, которые уложатся в эту сумму.\nК сожалению временно поддерживается только основное меню McDonalds. Я работаю над этим.\n\nОтказ от ответственности:\nРазработчик бота не сотрудничает с ресторанами быстрого питания. Бот является неоффициальной разработкой. Цены взяты из открытых источников, обновляются раз в неделю и могут быть неактуальны. Сервис предоставляется пользователю \"как есть\", пользователь использует сервис на свое усмотрение и понимает возможные риски использования. Разработчик не несет ответственности за возможные последствия использования. Справка бота: /help",
		"error":"Неверный ввод, введите сумму в рублях на заказ или \"/help\"",	
		"process":processInput,
		"help":"Справка:\nВведите сумму в рублях, которую вы готовы потратить на заказ. Сумму необходимо вводить без указания валюты, кавычек или других символов. Если была введена сумма более 1000 рублей, она будет автоматически понижена ботом до 1000 рублей. Тратить более тысячи рублей на человека в ресторанах быстрого питания как минимум странно.\nСейчас поддерживается только основное меню ресторана McDonalds, в ближайшее вермя будет добавлена поддержка меню ресторана KFC\n\n/about - О возможностях бота\n/author - О разработчике\n/disclaimer - Отказ от ответственности",
		"disclaimer":"Отказ от ответственности:\nРазработчик бота не сотрудничает с ресторанами быстрого питания. Бот является неоффициальной разработкой. Цены взяты из открытых источников, обновляются раз в неделю и могут быть неактуальны. Сервис предоставляется пользователю \"как есть\", пользователь использует сервис на свое усмотрение и понимает возможные риски использования. Разработчик не несет ответственности за возможные последствия использования. Справка бота: /help",
		"about":"Бот поможет вам определиться с разнообразным выбором в фастфудах страны. Просто введите сумму в рублях, которую готовы потратить, и бот предложит несколько заказов, которые уложатся в эту сумму.\nПока что поддерживается только основное меню ресторана McDonalds, но бот быстро развивается.\n\n/disclaimer - отказ от ответственности",
		"author":"Главный и единственный разработчик:\n\nИмя: Александр\nАдрес для связи по любым вопросам: ffprice@inbox.ru\nВеб сайт: я работаю над этим."
}
#-----------------------------------



botsDict = {}
def addBotToDict(token, commandsDict):
	try:
		bot = telepot.Bot(token)
		botsDict[token] = [bot, commandsDict]
	except:
		log.warning("Can't add bot to bot dictionary")

addBotToDict("309603787:AAHB6uOEc9aRuQfUoYrjW_we4zF8LJIu82g", commands)

class TelegramView(View):
	
	def processCommand(self, chat_id, text):
		if text in self.commandsDict.keys() and text != "process":
			tmp = self.commandsDict.get(text)
			if isinstance(tmp, str):
				self.activeBot.sendMessage(chat_id, tmp)
			elif callable(tmp):
				tmp(chat_id)
			else:
				self.activeBot.sendMessage(chat_id, self.commandsDict.get('error'))
		else:
			self.activeBot.sendMessage(chat_id, self.commandsDict.get('error') + text)
	
	def processRequest(self, payload):
		msg = payload['message']
		if 'entities' in msg.keys():
			ents = msg['entities']
			if ents[0]['type'] == 'bot_command':
				self.processCommand(msg['chat']['id'], msg['text'][1:])
				return
		
		self.commandsDict.get("process")(self.activeBot, msg, self.commandsDict.get("error"))
	
	def post(self, request, token):
		if not (token in botsDict.keys()):
			return HttpResponseForbidden('Invalid bot token')
		self.activeBot = botsDict.get(token)[0]
		self.commandsDict = botsDict.get(token)[1]
		raw = request.body.decode('utf-8')
		
		try:
			payload = json.loads(raw)
		except ValueError:
			return HttpResponseBadRequest('Invalid request body')
		else:
			try:
				self.processRequest(payload)
			except KeyError:
				return HttpResponseBadRequest('KeyError in body')
		
		response = JsonResponse({})
		response.status_code = 200
		return response
	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(TelegramView, self).dispatch(request, *args, **kwargs)

	
		
