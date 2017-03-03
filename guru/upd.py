# -*- coding:utf-8 -*-

import sys
import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "burgerguru.settings")
django.setup()

from guru.updater.loader import MacDownloader, KfcDownloader
from guru.updater.parser import MacParser, KfcParser
from guru.updater.resturants import updateAll

updateAll()

if "kfc" in sys.argv:
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
    if "-load" in sys.argv:
        kfc.download_main()
    if "-upd" in sys.argv:
        upd.parse_main()
    if "-load" in sys.argv:
        kfc.download_cats(upd.cats)
    if "-upd" in sys.argv:
        upd.parse_cats()
    if "-load" in sys.argv:
        prodLinks = []
        for key in upd.products.keys():
            for val in upd.products.get(key):
                prodLinks.append(val[1])
        kfc.download_cats(prodLinks)
    if "-upd" in sys.argv:
        upd.parse_prices()
        upd.update_django()
    if "-prior" in sys.argv:
        upd.set_priority(prior)

elif "mac" in sys.argv:
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

    if "-load" in sys.argv:
        mac.download_main()
    if "-upd" in sys.argv:
        upd.parse_main()
    if "-load" in sys.argv:
        mac.download_prices(upd.products)
    if "-upd" in sys.argv:
        upd.parse_prices()
        upd.update_django()
    if "-prior" in sys.argv:
        upd.set_priority(priorDict)
