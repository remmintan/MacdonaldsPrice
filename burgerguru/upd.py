# -*- coding:utf-8 -*-

import sys
import os

from updater.loader import Downloader, MacDownloader
from updater.parser import MacParser
from updater import resturants

upd = MacParser()
mac = MacDownloader()

if "-load" in sys.argv:
	mac.downloadMain()

if "-upd" in sys.argv:
	upd.parseMain()
	
if "-load" in sys.argv:
	mac.downloadPrices(upd.products)

if "-upd" in sys.argv:
	upd.parsePrices()
	resturants.updateAll()
	upd.updateDjango()

priorDict = {
	"Сандвичи":1,
	"Напитки": 2,
	"Кофе, чай": 2,
	"Картофель": 3,
	"Десерты":3,
	"Салаты":3,
	"Соусы":9
}
if "-prior" in sys.argv:
	upd.setPrioty(priorDict)
