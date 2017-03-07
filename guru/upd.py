# -*- coding:utf-8 -*-

import sys
import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "burgerguru.settings")
django.setup()

from updater.loader import MacDownloader, KfcDownloader, BKDownloader
from updater.parser import MacParser, KfcParser, BKParser
from updater.resturants import update_all

update_all()

commands = input("What should I do?").split()

if "kfc" in commands:
    prior = {
        u"Сaндвичи": 1,
        u"Баcкеты": 1,
        u"Курица": 1,
        u"Напитки": 2,
        u"Десерты": 3,
        u"Cалаты": 3,
        u"Снэки": 3,
        u"Соусы": 9,
    }

    kfc = KfcDownloader()
    upd = KfcParser()
    if "-load" in commands:
        kfc.download_main()
    if "-upd" in commands:
        upd.parse_main()
    if "-load" in commands:
        kfc.download_cats(upd.cats)
    if "-upd" in commands:
        upd.parse_cats()
    if "-load" in commands:
        prodLinks = []
        for key in upd.products.keys():
            for val in upd.products.get(key):
                prodLinks.append(val[1])
        kfc.download_cats(prodLinks)
    if "-upd" in commands:
        upd.parse_prices()
        upd.update_django()
    if "-prior" in commands:
        upd.set_priority(prior)

if "mac" in commands:
    mac = MacDownloader()
    upd = MacParser()

    priorDict = {
        u"Сандвичи": 1,
        u"Напитки": 2,
        u"Кофе, чай": 2,
        u"Картофель": 3,
        u"Десерты": 3,
        u"Салаты": 3,
        u"Соусы": 9
    }

    if "-load" in commands:
        mac.download_main()
    if "-upd" in commands:
        upd.parse_main()
    if "-load" in commands:
        mac.download_prices(upd.products)
    if "-upd" in commands:
        upd.parse_prices()
        upd.update_django()
    if "-prior" in commands:
        upd.set_priority(priorDict)

if "bk" in commands:
    bk = BKDownloader()
    upd = BKParser()

    priorDict = {
        u"Вопперы и Бургеры": 1,
        u"Гарниры": 3,
        u"Снеки": 3,
        u"Салаты": 3,
        u"Напитки": 2,
        u"Десерты": 3,
    }

    if "-load" in commands:
        bk.dowload_main()
    if "-upd" in commands:
        upd.parse_main()
        upd.mirror_check()
    if "-prior" in commands:
        upd.set_priority(priorDict)
