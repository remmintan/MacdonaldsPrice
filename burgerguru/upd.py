# -*- coding:utf-8 -*-

import sys
import os

from updater.loader import Downloader
from updater.parser import Updater
from updater import resturants

proxyList = [
	"95.31.29.209:3128",
	"77.50.220.92:8080",
	"91.217.42.2:8080",
	"62.122.100.90:8080",
	"62.165.42.170:8080",
	"83.169.202.2:3128",
	"82.146.52.210:8118"
]

dwnld = Downloader(proxyList)
upd = Updater()
if "-load" in sys.argv:
	dwnld.downloadMain()
if "-upd" in sys.argv:
	upd.parseMain("mac")
if "-load" in sys.argv:
	dwnld.downloadEachPrice(upd.products)
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
