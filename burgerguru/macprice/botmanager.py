# -*- coding: utf-8 -*-

import telepot
import controllers

import logging

class FFPriceBot:
	
	def __init__(self, token):
		self.log = logging.getLogger('django')
		self.__bot = telepot.Bot(token)
		self.__commands = {
			"start":self.start,
			"startText":"Введите сумму (в рублях), которую вы готовы потратить и я подскажу вам несколько заказов, которые уложатся в эту сумму.\nК сожалению, временно поддерживается только основное меню McDonalds. Я работаю над этим.",	
			"help":"Справка:\nВведите сумму в рублях, которую вы готовы потратить на заказ. Сумму необходимо вводить без указания валюты, кавычек или других символов. Если была введена сумма более 1000 рублей, она будет автоматически понижена ботом до 1000 рублей. Тратить более тысячи рублей на человека в ресторанах быстрого питания как минимум странно.\nСейчас поддерживается только основное меню ресторана McDonalds, в ближайшее вермя будет добавлена поддержка меню ресторана KFC\n\n/about - О возможностях бота\n/author - О разработчике\n/disclaimer - Отказ от ответственности",
			"disclaimer":"Отказ от ответственности:\nРазработчик бота не сотрудничает с ресторанами быстрого питания. Бот является неоффициальной разработкой. Цены взяты из открытых источников, обновляются раз в неделю и могут быть неактуальны. Сервис предоставляется пользователю \"как есть\", пользователь использует сервис на свое усмотрение и понимает возможные риски использования. Разработчик не несет ответственности за возможные последствия использования. Справка бота: /help",
			"about":"Бот поможет вам определиться с разнообразным выбором в фастфудах страны. Просто введите сумму в рублях, которую готовы потратить, и бот предложит несколько заказов, которые уложатся в эту сумму.\nПока что поддерживается только основное меню ресторана McDonalds, но бот быстро развивается.\n\n/disclaimer - отказ от ответственности",
			"author":"Главный и единственный разработчик:\n\nИмя: Александр\nАдрес для связи по любым вопросам: ffprice@inbox.ru\nВеб сайт: я работаю над этим."
		}
		
		self.__errors={
			"nocommand":"Команда не найдена",
			"basestart":"Неверный ввод:\n",
			"baseend":"\nСправка: /help",
			"notanumber":"Отправьте только сумму(в рублях), которую вы готовы потратить на заказ.",
			"toomany":"Вы ввели несколько чисел, мне нужно только одно: сумма (в рублях) которую вы готовы потратить на заказ.",
		}
		
		self.__info = {
			"mt10000":"Сумму нужно указывать в Российских рублях. Кажется вы ошиблись. (Сумма снижена до 1000)",
			"mt5000":"Вау! Сколько денег! Может быть посоветовать вам ближайший ресторан? (Сумма снижена до 1000)",
			"mt1000":"1000 рублей более чем достаточно, что бы наесться в макдоналдсе. (Сумма снижена до 1000)"
		}
	
	def start(self):
		message = self.__commands['startText']
		message += "\n\n"+self.__commands['disclaimer']
		self.sendMessage(message)
	
	def sendMessage(self, text):
		self.__bot.sendMessage(self.__chat_id, text)
	
	def sendError(self, errType):
		errorText = self.__errors['basestart']
		if errType in self.__errors:
			errorText += self.__errors[errType]
		errorText += self.__errors['baseend']
		self.sendMessage(errorText)
		
	
	def processRequest(self, payload):
		self.__msg = payload['message']
		self.__chat_id = self.__msg['chat']['id']
		
		if 'entities' in self.__msg.keys():
			if self.__msg['entities'][0]['type'] == 'bot_command':
				self.processCommand()
			else:
				self.sendError('notanumber')
				return
		else:
			self.processInput()
				
	def processCommand(self):
		text = self.__msg['text'][1:]
		if text in self.__commands.keys():
			command = self.__commands[text]
			if callable(command):
				command()
				return
				
			self.sendMessage(command)
		else:
			self.sendError('nocommand')
			
	def processInput(self):
		summ = 0
		text = self.__msg['text']
		arrText = text.split()
		try:
			for strr in arrText:
				int(float(strr))
			if len(arrText)>1:
				self.sendError('toomany')
				return
		except:
			self.sendError('notanumber')
			return
		
		try:
			summ = int(float(text))
		except:
			self.sendError('notanumber')
			return;
		
		#input is ok. Processing order
		self.processOrder(summ)
		
	def processOrder(self, summ):
		self.log.info("I'm here!")
		if summ>10000:
			self.sendMessage(self.__info['mt10000'])
		elif summ>5000:
			self.sendMessage(self.__info['mt5000'])
		elif summ>1000:
			self.sendMessage(self.__info['mt1000'])
		
		if summ>1000:
			summ = 1000
		
		orderText = controllers.createOrder(summ)
		self.sendMessage(orderText)
			

