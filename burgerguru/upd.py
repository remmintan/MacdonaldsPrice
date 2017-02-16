# -*- coding:utf-8 -*-

import sys
import os

from updater.loader import Downloader, MacDownloader, KfcDownloader
from updater.parser import MacParser, KfcParser
from updater.resturants import updateAll

updateAll()

if "kfc" in sys.argv:
	prior = {
		u"Сaндвичи":1,
		u"Баcкеты":1,
		u"Курица":1,
		u"Напитки":2,
		u"Десерты":3,
		u"Cалаты":3,
		u"Снэки":3,
	}
	
	kfc = KfcDownloader()
	upd = KfcParser()
	if "-load" in sys.argv:
		kfc.downloadMain()
	if "-upd" in sys.argv:
		upd.parseMain()
	if "-load" in sys.argv:
		kfc.downloadCats(upd.cats)
	if "-upd" in sys.argv:
		upd.parseCats()
	if "-load" in sys.argv:
		prodLinks = []
		for key in upd.products.keys():
			for val in upd.products.get(key):
				prodLinks.append(val[1])
		kfc.downloadCats(prodLinks)
	if "-upd" in sys.argv:
		upd.parsePrices()
		upd.updateDjango()
	if "-prior" in sys.argv:
		upd.setPriority(prior)

elif "mac" in sys.argv:
	mac = MacDownloader()
	upd = MacParser()
	
	priorDict = {
		u"Сандвичи":1,
		u"Напитки": 2,
		u"Кофе, чай": 2,
		u"Картофель": 3,
		u"Десерты":3,
		u"Салаты":3,
		u"Соусы":9
	}
	
	if "-load" in sys.argv:
		mac.downloadMain()
	if "-upd" in sys.argv:
		upd.parseMain()
	if "-load" in sys.argv:
		mac.downloadPrices(upd.products)
	if "-upd" in sys.argv:
		upd.parsePrices()
		upd.updateDjango()
	if "-prior" in sys.argv:
		upd.setPriority(priorDict)
	

