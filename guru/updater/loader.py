# -*- coding: utf-8 -*-

import sys
import time
import urllib3
from urllib3 import ProxyManager

urllib3.disable_warnings()


class Downloader:
    def __init__(self, proxy_list):
        self.__proxyCounter = 0
        self.__proxyList = proxy_list
        self.__http = ProxyManager("http://" + self.__proxyList[self.__proxyCounter])

    def try_download(self, url, tries=0):
        try:
            r = self.__http.request('GET', url)
        except:
            if tries > 2:
                print("To many tries, updating proxy...")
                self.update_proxy()
                r = self.try_download(url)
            else:
                print("Error while downloading from \'%s\'. Trying again in 3 secs... [%d]" % (url, tries + 1))
                time.sleep(3)
                r = self.try_download(url, tries + 1)
        return r

    def update_proxy(self):
        self.__proxyCounter += 1
        if self.__proxyCounter >= len(proxyList):
            self.__proxyCounter = 0
        self.__http = ProxyManager("http://" + self.__proxyList[self.__proxyCounter])

    def download_to_file(self, url, file_adress, tries=0):
        print("Start downloading from: '{0}'".format(url))
        r = self.try_download(url)
        if r.status == 200:
            print("Downloaded. Saving to '{0}'".format(file_adress))
            f = open(file_adress, 'wb')
            f.write(r.data)
            f.close()
        elif r.status // 100 == 5:
            print("Something wrong with server (%s). Waiting 2 secs and trying again... [%d]" % (r.status, tries + 1))
            time.sleep(2)
            if tries < 5:
                self.download_to_file(url, file_adress, tries + 1)
            else:
                print("Too many tries. Aborting! Try to start update later")
                return -1
        else:
            print("Wrong response status: {0}".format(r.status))


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


class MacDownloader:
    siteName = "mcdonalds.ru"
    folder = "macdata"

    def download_main(self):
        url = "http://" + self.siteName + "/products"
        file_adress = self.folder + "/main.html"
        dwnld.download_to_file(url, file_adress)

    def download_prices(self, arr):
        for key in arr.keys():
            for link in arr.get(key):
                url = "http://%s%s" % (self.siteName, link[1])
                file_adress = self.folder + link[1] + ".html"
                if dwnld.download_to_file(url, file_adress) == -1:
                    print("Aborting...")
                    sys.exit()


class KfcDownloader:
    siteName = "www.kfc.ru"
    folderName = "kfcdata"

    def download_main(self):
        url = "https://" + self.siteName
        file_adress = self.folderName + "/main.html"
        dwnld.download_to_file(url, file_adress)

    def download_cats(self, links):
        for link in links:
            file_adress = self.folderName + link + ".html"
            url = "https://" + self.siteName + link
            dwnld.download_to_file(url, file_adress)
