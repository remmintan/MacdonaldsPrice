# -*- coding: utf-8 -*-

import logging
import telepot
from django.utils import timezone
from telepot.exception import TelegramError, TooManyRequestsError
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

import sys

import time

from macprice import controllers
from macprice.models import User, Chat


class FFPriceBot:
    def __init__(self, token):
        self.__user = None
        self.__msg = ""
        self.__chat_id = ""
        self.__user_id = ""

        self.log_info = logging.getLogger('django')
        self.log_error = logging.getLogger('django.request')
        self.__bot = telepot.Bot(token)
        self.__commands = {
            "start": self.start,
            "startText": "Введите сумму (в рублях), которую вы готовы потратить и я подскажу вам несколько заказов, которые уложатся в эту сумму.",
            "help": self.helpM,
            "disclaimer": "*Отказ от ответственности:*\nРазработчик бота не сотрудничает с ресторанами быстрого питания. Бот является *неоффициальной* разработкой. \nЦены взяты из открытых источников, обновляются раз в неделю и *могут быть неактуальны*. \nСервис предоставляется пользователю \"как есть\", пользователь использует сервис на свое усмотрение, разработчик не несет ответственности за возможные последствия использования. \nСправка бота: /help",
            "about": "Этот бот поможет вам определиться с разнообразным выбором в ресторанах быстрого питания. Просто выберите один из доступных ресторанов быстрого питания и введите сумму в рублях, которую вы готовы потратить на заказ. Бот предложит несколько вариантов заказа, которые уложатся в эту сумму.\n\n/disclaimer - отказ от ответственности",
            "author": "*Главный и единственный разработчик:*\nИмя: Александр\nE-mail: ffprice@inbox.ru\nTelegram: @alexmojar\nПоддержать разработчика: /donate\n\n*Фотография бота:*\nЛицензия: CC BY 2.0\nАвтор: Agustin Nieto:\nИсточник: [flickr](https://flic.kr/p/nSseJW)",
            "donate": "*Поддержать:*\n Спасибо, что заинтересовались поддержкой бота!\n Бот располагается на VPS от DigitalOcean (5-10$/мес.) и не приносит никакой прибыли.\n Если вы считаете, что любая работа должна оплачиваться или хотите поддержать мои разработки, просто пожертвуйте любую сумму на развитие бота. \n\n*Яндекс Деньги:* 410012477007394 или [перевод](https://money.yandex.ru/to/410012477007394)\n*Paypal:* [перевод](https://www.paypal.me/alexmojar/100)\n*Банковская карта:* 5278 8300 6712 3129\n\nЛюбая другая помощь или предложения приветствуются. Контакты: /author\n\nСпасибо! Без вашей поддержки я бы не справился!",
            "otherff": self.changeResturan
        }

        self.__errors = {
            "nocommand": "Команда не найдена",
            "basestart": "Неверный ввод:\n",
            "baseend": "\nСправка: /help",
            "notanumber": "Отправьте только сумму(в рублях), которую вы готовы потратить на заказ.",
            "toomany": "Вы ввели несколько чисел, мне нужно только одно: сумма (в рублях) которую вы готовы потратить на заказ.",
            "notenoughmoney": "Вы ввели очень маленькую сумму, на нее невозможно составить полноценный заказ. Минимальная сумма: 50 руб.",
            "firstorder": "У вас еще не было ни одного заказа, сделайте свой первый заказ, отправив боту сумму, которую вы готовы потратить на заказ.",
        }

        self.__info = {
            "mt10000": "Сумму нужно указывать в Российских рублях. Кажется вы ошиблись. (Сумма снижена до тысячи)",
            "mt5000": "Вау! Сколько денег! Может быть посоветовать вам ближайший ресторан? (Сумма снижена до тысячи)",
            "mt1000": "Тысячи рублей более чем достаточно для ресторанов быстрого питания. (Сумма снижена до тысячи)",
            "havenotchoosen": "Выберите пожалуйста ресторан из списка:"
        }

        self.__textCommands = {
            u"Выбрать другой ресторан": self.changeResturan,
            u"Другие варианты заказа": self.repeatOrder,
        }

        self.__resturants = controllers.createDictResturants()

    def repeatOrder(self):
        if self.__user.lastSum == 0:
            self.sendError("firstorder")
        else:
            ls = self.__user.lastSum
            orderText = u"Другие варианты заказа на сумму %d руб.\n\n" % ls
            orderText += controllers.createOrder(ls, self.__user.resturant)
            self.sendMessage(orderText, self.getKeyboard([u"Другие варианты заказа", u"Выбрать другой ресторан"]))

    def changeResturan(self):
        self.__user.haveChosen = False
        self.__user.save()

        message = self.__info["havenotchoosen"]
        self.sendMessage(message, self.getKeyboard(self.__resturants.keys()))

    def helpM(self):
        helpArray = ["*Справка:*\n"
                     "Введите сумму в рублях, которую вы готовы потратить на заказ. Сумму необходимо вводить без указания валюты, кавычек или других символов. Например: Если вы хотите, чтобы бот предложил зказазы, уложившись в 350 рублей, вам надо отправить боту просто число 350.",
                     "Если была введена сумма более 1000 рублей, она будет автоматически понижена ботом до 1000 рублей.",
                     "Кнопка \"Другие варианты заказа\" формирует заказы на сумму последнего Вашего заказа.\n",
                     "/about - О возможностях бота",
                     "/otherff - Выбрать другой ресторан",
                     "/donate - Поддержать развитие бота",
                     "/author - О разработчике",
                     "/disclaimer - Отказ от ответственности",
                     ]
        helpText = "\n".join(helpArray)
        self.sendMessage(helpText)

    @staticmethod
    def getKeyboard(btnsArr):
        keyboardButtons = []
        for button in btnsArr:
            keyboardButtons.append([KeyboardButton(text=button)])
        keyboard = ReplyKeyboardMarkup(keyboard=keyboardButtons, resize_keyboard=True)
        return keyboard

    def start(self):
        self.__user.haveChosen = False
        self.__user.save()

        message = self.__commands['disclaimer']
        message += "\n\n" + self.__info["havenotchoosen"]
        self.sendMessage(message, self.getKeyboard(self.__resturants.keys()))

    def start2(self):
        keyboard = self.getKeyboard([u"Выбрать другой ресторан"])
        self.sendMessage(self.__commands['startText'], keyboard)

    def sendMessage(self, text, keyboard=None):
        try:
            if keyboard is None:
                self.__bot.sendMessage(self.__chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                self.__bot.sendMessage(self.__chat_id, text, parse_mode='Markdown', reply_markup=keyboard,
                                       disable_web_page_preview=True)
            self.log_info.info("Just sent message to %s. Everything ok!" % self.__chat_id)
        except TooManyRequestsError as e:
            wait_time = e.json['parameters']['retry_after']
            self.log_error.error('Too many requests! Wait time %i' % wait_time)
            time.sleep(wait_time+1)
            self.sendMessage(text, keyboard)
        except TelegramError as e:
            self.log_error.error('Some Telegram error was occurate! %s' % e.description)

    def sendError(self, errType):
        errorText = self.__errors['basestart']
        if errType in self.__errors:
            errorText += self.__errors[errType]
        errorText += self.__errors['baseend']
        self.sendMessage(errorText)

    def updateUser(self):
        username = self.__msg['from']['first_name']
        if 'last_name' in self.__msg['from'].keys():
            usersurname = self.__msg['from']['last_name']
        else:
            usersurname = ""

        if not User.objects.filter(pk=self.__user_id).exists():
            self.__user = User(id=self.__user_id, name=username, surname=usersurname)
            self.__user.save()
        else:
            self.__user = User.objects.filter(pk=self.__user_id)[0]
            self.__user.update(username, usersurname)

    def updateChat(self):
        if not Chat.objects.filter(pk=self.__chat_id).exists():
            chat_type = self.__msg['chat']['type']

            chat = Chat(id=self.__chat_id, chatType=chat_type)
            chat.save()

    def processRequest(self, payload):

        self.__msg = payload['message']
        self.__chat_id = self.__msg['chat']['id']
        self.__user_id = self.__msg['from']['id']

        self.updateUser()
        self.updateChat()

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
        text = self.__msg['text']

        if text in self.__resturants.keys():
            self.__user.resturant = self.__resturants[text]
            self.__user.haveChosen = True
            self.__user.save()
            self.start2()
            return
        elif not self.__user.haveChosen:
            self.sendMessage(self.__info['havenotchoosen'], self.getKeyboard(self.__resturants.keys()))
            return
        elif text in self.__textCommands.keys():
            self.__textCommands[text]()
            return

        arrText = text.split()
        try:
            for strr in arrText:
                int(float(strr))
            if len(arrText) > 1:
                self.sendError('toomany')
                return
        except:
            self.sendError('notanumber')
            return

        try:
            summ = int(float(text))
        except:
            self.sendError('notanumber')
            return

            # input is ok. Processing order
        if Chat.objects.filter(pk=self.__chat_id).exists():
            chat = Chat.objects.filter(pk=self.__chat_id)[0]
            chat.requests += 1
            chat.lastRequest = timezone.now()
            chat.save()
        self.processOrder(summ)

    def processOrder(self, summ):
        if summ < 50:
            self.sendError('notenoughmoney')
            return

        if summ > 10000:
            self.sendMessage(self.__info['mt10000'])
        elif summ > 5000:
            self.sendMessage(self.__info['mt5000'])
        elif summ > 1000:
            self.sendMessage(self.__info['mt1000'])

        if summ > 1000:
            summ = 1000

        self.__user.lastSum = summ
        self.__user.save()

        orderText = controllers.createOrder(summ, self.__user.resturant)
        self.sendMessage(orderText, self.getKeyboard([u"Другие варианты заказа", u"Выбрать другой ресторан"]))
