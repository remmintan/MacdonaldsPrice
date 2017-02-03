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
		size = self.size
		
		if self.summ<50:
			size=1
		
		range = self.getRangeForMoney(group, size)
		if range == -1:
			return -1
		products = Product.objects.filter(group=group, price__gte=range[0]).filter(price__lte=range[1])
		if len(products) == 1:
			
			return products[0]
		elif len(products)==0:
			return -1
		else:
			prod = products[randint(0, len(products)-1)]
			
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
		l1 = Product.objects.filter(group=ProductGroup.objects.get(group_name="Кофе, чай")).order_by('price')
		
		ord = Order(sum)
		ord.compileOrder(int(int(sum)*0.04))
		products=ord.products
		
		return render(request, 'macprice/index.html', { 'l1':l1, 'prodList':products, 'var':int(sum)-int(ord.summ)})

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
	ord = Order(summ)
	ord.compileOrder(int(int(summ)*0.04))
	responseText = "Ваш заказ. Вариант№1:\n"
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
		responseText+=s
	responseText+="Итого: %d"%sum
	bot.sendMessage(chat_id, responseText)

commands = {
		"start":"Введите сумму (в рублях), которую вы готовы потратить и я подскажу вам несколько заказов, которые уложатся в эту сумму.\nК сожалению временно поддерживается только основное меню McDonalds. Мы работаем над этим.",
		"error":"Неверный ввод, введите сумму в рублях на заказ или \"/help\"",	
		"process":processInput,
		
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

	
		
