# -*- coding: utf-8 -*-

import logging
import telepot
from django.utils import timezone
from telepot.exception import TelegramError, TooManyRequestsError
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from random import randint
from random import random

import numpy
from macprice.models import ProductGroup, Product, User, Resturant, Chat


def createDictResturants():
    diction = {}
    for part in User.RESTURANT_CHOICES:
        diction[part[1]] = part[0]
    return diction


class FFPriceBot:
    # Create your views here.
    bots_dict = {
        # prodaction
        "309603787:AAHB6uOEc9aRuQfUoYrjW_we4zF8LJIu82g": telepot.Bot("309603787:AAHB6uOEc9aRuQfUoYrjW_we4zF8LJIu82g"),
        # development
        "279023466:AAHmCU7BcKcrR32Sw97esrCfa7C0oDykz9M": telepot.Bot("279023466:AAHmCU7BcKcrR32Sw97esrCfa7C0oDykz9M"),
    }

    types = {
        "N": u"",
        "S": u" (мал.)",
        "M": u" (станд.)",
        "L": u" (бол.)",
        "X": u" (оч.бол.)",
    }

    def __init__(self):
        self.__user = None
        self.__msg = ""
        self.__chat_id = ""
        self.__user_id = ""

        self.log_info = logging.getLogger('django')
        self.log_error = logging.getLogger('django.request')
        self.__commands = {
            "start": self.start,
            "startText": "Введите сумму (в рублях), которую вы готовы потратить и я подскажу вам несколько заказов, которые уложатся в эту сумму.",
            "help": self.help_m,
            "disclaimer": "*Отказ от ответственности:*\nРазработчик бота не сотрудничает с ресторанами быстрого питания. Бот является *неоффициальной* разработкой. \nЦены взяты из открытых источников, обновляются раз в неделю и *могут быть неактуальны*. \nСервис предоставляется пользователю \"как есть\", пользователь использует сервис на свое усмотрение, разработчик не несет ответственности за возможные последствия использования. \nСправка бота: /help",
            "about": "Этот бот поможет вам определиться с разнообразным выбором в ресторанах быстрого питания. Просто выберите один из доступных ресторанов быстрого питания и введите сумму в рублях, которую вы готовы потратить на заказ. Бот предложит несколько вариантов заказа, которые уложатся в эту сумму.\n\n/disclaimer - отказ от ответственности",
            "author": "*Главный и единственный разработчик:*\nИмя: Александр\nE-mail: ffprice@inbox.ru\nTelegram: @alexmojar\nПоддержать разработчика: /donate\n\n*Фотография бота:*\nЛицензия: CC BY 2.0\nАвтор: Agustin Nieto:\nИсточник: [flickr](https://flic.kr/p/nSseJW)",
            "donate": "*Поддержать:*\n Спасибо, что заинтересовались поддержкой бота!\n Бот располагается на VPS от DigitalOcean (5-10$/мес.) и не приносит никакой прибыли.\n Если вы считаете, что любая работа должна оплачиваться или хотите поддержать мои разработки, просто пожертвуйте любую сумму на развитие бота. \n\n*Яндекс Деньги:* 410012477007394 или [перевод](https://money.yandex.ru/to/410012477007394)\n*Paypal:* [перевод](https://www.paypal.me/alexmojar/100)\n*Банковская карта:* 5278 8300 6712 3129\n\nЛюбая другая помощь или предложения приветствуются. Контакты: /author\n\nСпасибо! Без вашей поддержки я бы не справился!",
            "otherff": self.change_resturan
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
            u"Выбрать другой ресторан": self.change_resturan,
            u"Другие варианты заказа": self.repeat_order,
        }

        self.__resturants = createDictResturants()

    def set_bot(self, token):
        self.__bot = self.bots_dict[token]

    def repeat_order(self):
        if self.__user.lastSum == 0:
            self.send_error("firstorder")
        else:
            ls = self.__user.lastSum
            order_text = u"Другие варианты заказа на сумму %d руб.\n\n" % ls
            order_text += self.create_order(ls)
            self.send_message(order_text, self.get_keyboard([u"Другие варианты заказа", u"Выбрать другой ресторан"]))

    def change_resturan(self):
        self.__user.haveChosen = False
        self.__user.save()

        message = self.__info["havenotchoosen"]
        self.send_message(message, self.get_keyboard(self.__resturants.keys()))

    def help_m(self):
        help_array = ["*Справка:*\n"
                     "Введите сумму в рублях, которую вы готовы потратить на заказ. Сумму необходимо вводить без указания валюты, кавычек или других символов. Например: Если вы хотите, чтобы бот предложил зказазы, уложившись в 350 рублей, вам надо отправить боту просто число 350.",
                     "Если была введена сумма более 1000 рублей, она будет автоматически понижена ботом до 1000 рублей.",
                     "Кнопка \"Другие варианты заказа\" формирует заказы на сумму последнего Вашего заказа.\n",
                     "/about - О возможностях бота",
                     "/otherff - Выбрать другой ресторан",
                     "/donate - Поддержать развитие бота",
                     "/author - О разработчике",
                     "/disclaimer - Отказ от ответственности",
                     ]
        help_text = "\n".join(help_array)
        self.send_message(help_text)

    @staticmethod
    def get_keyboard(btns_arr):
        keyboard_buttons = []
        for button in btns_arr:
            keyboard_buttons.append([KeyboardButton(text=button)])
        keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)
        return keyboard

    def start(self):
        self.__user.haveChosen = False
        self.__user.save()

        message = self.__commands['disclaimer']
        message += "\n\n" + self.__info["havenotchoosen"]
        self.send_message(message, self.get_keyboard(self.__resturants.keys()))

    def start2(self):
        keyboard = self.get_keyboard([u"Выбрать другой ресторан"])
        self.send_message(self.__commands['startText'], keyboard)

    def send_message(self, text, keyboard=None):
        try:
            if keyboard is None:
                self.__bot.sendMessage(self.__chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                self.__bot.sendMessage(self.__chat_id, text, parse_mode='Markdown', reply_markup=keyboard,
                                       disable_web_page_preview=True)
        except TooManyRequestsError as e:
            wait_time = e.json['parameters']['retry_after']
            self.log_error.error('Too many requests! Wait time %i' % wait_time)
            # time.sleep(wait_time+1)  # this system is shit. it shuts down th whole server
            # self.send_message(text, keyboard)
        except TelegramError as e:
            self.log_error.error('Some Telegram error was occurate! %s' % e.description)

    def send_error(self, err_type):
        error_text = self.__errors['basestart']
        if err_type in self.__errors:
            error_text += self.__errors[err_type]
        error_text += self.__errors['baseend']
        self.send_message(error_text)

    def update_user(self):
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

    def update_chat(self):
        if not Chat.objects.filter(pk=self.__chat_id).exists():
            chat_type = self.__msg['chat']['type']

            chat = Chat(id=self.__chat_id, chatType=chat_type)
            chat.save()

    def process_request(self, payload):

        self.__msg = payload['message']
        self.__chat_id = self.__msg['chat']['id']
        self.__user_id = self.__msg['from']['id']

        self.update_user()
        self.update_chat()

        if 'entities' in self.__msg.keys():
            if self.__msg['entities'][0]['type'] == 'bot_command':
                self.process_command()
            else:
                self.send_error('notanumber')
                return
        else:
            self.process_input()

    def process_command(self):
        text = self.__msg['text'][1:]
        if text in self.__commands.keys():
            command = self.__commands[text]
            if callable(command):
                command()
                return

            self.send_message(command)
        else:
            self.send_error('nocommand')

    def process_input(self):
        text = self.__msg['text']

        if text in self.__resturants.keys():
            self.__user.resturantt = self.__resturants[text]
            self.__user.haveChosen = True
            self.__user.save()
            self.start2()
            return
        elif not self.__user.haveChosen:
            self.send_message(self.__info['havenotchoosen'], self.get_keyboard(self.__resturants.keys()))
            return
        elif text in self.__textCommands.keys():
            self.__textCommands[text]()
            return

        arr_text = text.split()
        try:
            for strr in arr_text:
                int(float(strr))
            if len(arr_text) > 1:
                self.send_error('toomany')
                return
        except:
            self.send_error('notanumber')
            return

        try:
            summ = int(float(text))
        except:
            self.send_error('notanumber')
            return

            # input is ok. Processing order
        if Chat.objects.filter(pk=self.__chat_id).exists():
            chat = Chat.objects.filter(pk=self.__chat_id)[0]
            chat.requests += 1
            chat.lastRequest = timezone.now()
            chat.save()
        self.process_order(summ)

    def process_order(self, summ):
        if summ < 50:
            self.send_error('notenoughmoney')
            return

        if summ > 10000:
            self.send_message(self.__info['mt10000'])
        elif summ > 5000:
            self.send_message(self.__info['mt5000'])
        elif summ > 1000:
            self.send_message(self.__info['mt1000'])

        if summ > 1000:
            summ = 1000

        self.__user.lastSum = summ
        self.__user.save()

        orderText = self.create_order(summ)
        self.send_message(orderText, self.get_keyboard([u"Другие варианты заказа", u"Выбрать другой ресторан"]))

    def create_order(self, summ):
        response_text = ""
        prod_check_array = []
        order_counter = 0
        attempts = 0
        # print "NEW ORDER ---------------------------------------------"

        for i in range(1, 4):
            order = Order(summ, Resturant.objects.get(short_name=self.__user.resturant), i)
            order.compileOrder(int(int(summ) * 0.08))
            if order.products in prod_check_array:
                i -= 1
                attempts += 1
                if attempts > 6:
                    break
                continue
            else:
                order_counter += 1

            order_text = u"*Ваш заказ. Вариант№%d:*\n" % order_counter
            counter = 0
            price_sum = 0
            ccal_sum = 0


            for prod in order.products:
                counter += 1
                price_sum += prod.price
                if self.__user.resturant == "mac":
                    ccal_sum += prod.ccal
                name = prod.product_name
                name += self.types[prod.product_type]
                s = u"{0}){1}: {2}руб.{3}ккал.\n".format(counter, name, prod.price,
                                                         prod.ccal) if self.__user.resturant == "mac" else u"{0}){1}: {2}руб.\n".format(
                    counter, name, prod.price)
                order_text += s
            if self.__user.resturant == "mac":
                order_text += u"*Калорийность: %i ккал.*\n" % ccal_sum
            order_text += u"*Итого: %i руб.*" % price_sum
            response_text += order_text + "\n\n"
            prod_check_array.append(order.products)

        response_text += u"Приятного аппетита!\nПри необходимости вы можете купить соусы на остаток денег."
        return response_text



class Order:
    def __init__(self, summ, resturant, orderType=2):
        self.__ordType = 1
        self.products = []
        self.groups = []
        self.prodNames = []
        self.sis = []
        self.attempts = 0

        self.summ = int(summ)
        self.rest = resturant
        self.productsPriority = []
        self.setOrdType(orderType)

    def ordType(self):
        return self.__ordType

    def setOrdType(self, value):
        self.__ordType = value
        if self.summ >= 500:
            if self.__ordType == 1:
                self.__ordType = 2

        if self.summ >= 750:
            self.__ordType = 3
        elif self.summ <= 150:
            if self.__ordType == 3:
                self.__ordType = 2
            if self.__ordType == 2:
                pass

    def getRangeForGroup(self, group, size):
        gp = [p.price for p in Product.objects.filter(group=group, price__gte=0, resturant=self.rest)]
        first = int(numpy.percentile(gp, 34))
        second = int(numpy.percentile(gp, 67))
        maximum = int(numpy.max(gp))
        minimum = int(numpy.min(gp))
        bot, top = (minimum, first - 1) if size == 1 else (first, second - 1) if size == 2 else (second, maximum)
        return [bot, top, top - bot]

    def getRangeForMoney(self, group, ordType):
        bt = self.getRangeForGroup(group, ordType)
        bot = bt[0]
        top = bt[1]

        if self.summ >= top:
            return [bot, top]
        elif self.summ < bot:
            if ordType != 1:
                ordType += -1
                return self.getRangeForMoney(group, ordType)
            else:
                return -1
        else:
            return [bot, self.summ]

    def getFromGroup(self, group, ordType):
        if self.summ < 50:
            ordType = 1

        priceRange = self.getRangeForMoney(group, ordType)
        if priceRange == -1:
            return -1
        products = Product.objects.filter(group=group, price__gte=priceRange[0], price__lte=priceRange[1])
        if len(products) == 1:
            self.sis.append(ordType)
            return products[0]
        elif len(products) == 0:
            if ordType == 1:
                return -1
            ordType += -1
            return self.getFromGroup(group, ordType)
        else:
            rnd = randint(0, len(products) - 1)
            prod = products[rnd]

            for i in range(0, len(products)):
                if not prod.product_name in self.prodNames:
                    break
                if rnd + i >= len(products):
                    rnd += -len(products)
                prod = products[rnd + i]

            self.sis.append(ordType)
            return prod

            # rewrite this shit!

    def getNewGroup(self, groups, rnd=-1, deepness=0):
        if rnd >= len(groups):
            rnd = 0
        offset = randint(0, len(groups) - 1) if rnd == -1 else rnd
        grp = groups[offset]
        if grp.group_name in self.groups and deepness < len(groups):
            return self.getNewGroup(groups, offset + 1, deepness + 1)
        elif deepness < len(groups):
            return grp
        else:
            # all groups were used
            return groups[randint(0, len(groups) - 1)]

    def addProduct(self):
        priority = self.getPriority()
        groups = ProductGroup.objects.filter(priority=priority, resturant=self.rest)
        group = self.getNewGroup(groups)
        prod = self.getFromGroup(group, self.__ordType)

        if prod != -1:
            self.summ += -prod.price
            self.products.append(prod)
            self.prodNames.append(prod.product_name)
            self.groups.append(group.group_name)
            self.productsPriority.append(priority)
            return 0
        else:
            if self.attempts > 10:
                return 0
            else:
                self.attempts += 1
                return -1

    def getPriority(self):
        for i in range(1, 4):
            if i not in self.productsPriority:
                return i

        return 1 if random() > 0.7 else 3

    def compileOrder(self, size):
        for i in range(0, size):
            i += self.addProduct()

            # print self.productsPriority
            # print self.sis
            # print



