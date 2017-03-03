# -*- coding: utf-8 -*-
import os
from bs4 import BeautifulSoup as BS
import django
from macprice.models import Product, ProductGroup, Resturant

os.environ["DJANGO_SETTINGS_MODULE"] = "guru.settings"
django.setup()


def create_soup_from_file(file_adress):
    print("Parsing file: %s" % file_adress)
    f = open(file_adress, 'rt', encoding='utf-8')
    data = f.read()
    soup = BS(data, 'html5lib')
    return soup


class MacParser:
    rest = "mac"
    folder = "macdata"
    products = {}

    def __init__(self):
        self.__resturan = Resturant.objects.get(short_name=self.rest)
        self.__resturan = Resturant.objects.get(short_name=self.rest)

    def parse_main(self):
        soup = create_soup_from_file(self.folder + '/main.html')
        products = soup.find('div', {'class': 'products__list'})
        row_list = products.findChildren('div', {'class': 'row'})
        for row in row_list:
            cat_title = row.findChildren('h2', {'class': 'products__cat-title'})[0]
            prod_links = row.findChildren('a', {'class': 'products__item-link'})
            self.products[cat_title.text.strip()] = []
            for a in prod_links:
                self.products[cat_title.text.strip()].append([a['title'].strip(), a['href'].strip()])
        print("Sucsess!")

    def parse_prices(self):
        for key in self.products.keys():
            new_array = []
            for link in self.products.get(key):
                file_adress = self.folder + link[1] + ".html"
                soup = create_soup_from_file(file_adress)
                prices = self.get_prices(soup)
                ccals = self.get_ccals(soup)
                new_array.append([link[0], prices[0], prices[1], ccals])
            self.products[key] = new_array

        print("Start govnocode section:")
        deserts = []
        for spec in self.products.get(u'Десерты'):
            if u'Молочный' in spec[0]:
                deserts.append(spec)

        for spec in deserts:
            self.products.get(u'Десерты').remove(spec)
            self.products.get(u'Напитки').append(spec)

    def get_prices(self, soup):
        price_list = soup.find_all('h4', {'class': 'product__show-price'})
        prod_type = "singular" if len(price_list) == 1 else "plural"
        price_arr = []
        for p in price_list:
            price_text = p.text.strip().split(' ')[0]
            if price_text == "":
                price_arr.append(-1)
            else:
                price_arr.append(int(price_text))

        return price_arr, prod_type

    def get_ccals(self, soup):
        tabs_content = soup.find_all('div', {'class': 'product__show-composition'})[0].findChildren('div',
                                                                                                    {
                                                                                                        'class': 'tabs__content'})[
            0]
        ccal_list = tabs_content.findChildren('div', {'class': 'tab'})
        ccal_arr = []
        for ccal in ccal_list:
            text = ccal.findChildren('tr')[2].findChildren('span')[0].text.strip()
            if text == "":
                ccal_arr.append(0)
            else:
                ccal_arr.append(int(float(text)))
        return ccal_arr

    # DJANGO STUFF below

    def update_django(self):

        for key in self.products.keys():
            if ProductGroup.objects.filter(group_name=key, resturant=self.__resturan).exists():
                pg = ProductGroup.objects.filter(group_name=key, resturant=self.__resturan)[0]
                print("Updating group: %s" % pg)
            else:
                pg = ProductGroup(group_name=key, resturant=self.__resturan)
                pg.save()
                print("Creating group: %s" % pg)

            prod_arr = self.products.get(key)
            for prod in prod_arr:
                if prod[2] == "singular":
                    if Product.objects.filter(product_name=prod[0], group=pg).exists():
                        p = Product.objects.filter(product_name=prod[0], group=pg)[0]
                        p.update(prod[1][0], self.rest, prod[3][0])
                    else:
                        p = Product(product_name=prod[0], group=pg, price=prod[1][0], resturant=self.__resturan,
                                    ccal=prod[3][0])
                        p.save()
                else:

                    self.update_plural(pg, "S", 0, prod)
                    if len(prod[1]) > 1:
                        self.update_plural(pg, "M", 1, prod)
                    if len(prod[1]) > 2:
                        self.update_plural(pg, "L", 2, prod)
                    if len(prod[1]) > 3:
                        self.update_plural(pg, "X", 3, prod)
            pg.save()
            print("Sucsess!")

        self.mirror_check()

    def mirror_check(self):
        print("Starting mirror check...")
        keys_arr = self.products.keys()
        for group in ProductGroup.objects.filter(resturant=self.__resturan):
            if group.group_name not in keys_arr:
                print("Deleting redundant group: %s" % group.group_name)
                group.delete()
                continue
            prod_arr = [prod[0] for prod in self.products.get(group.group_name)]
            for product in Product.objects.filter(group=group):
                if product.product_name not in prod_arr:
                    print("Deleting redundant object: %s" % product.product_name)
                    product.delete()

    def update_plural(self, pg, p_type, i, prod):
        if Product.objects.filter(product_name=prod[0], group=pg, product_type=p_type).exists():
            p = Product.objects.filter(product_name=prod[0], group=pg, product_type=p_type)[0]
            p.update(prod[1][i], self.rest, prod[3][i])
        else:
            p = Product(product_name=prod[0], group=pg, price=prod[1][i], product_type=p_type,
                        resturant=Resturant.objects.filter(short_name=self.rest)[0], ccal=prod[3][i])
            p.save()

    def set_priority(self, arr):
        groups = ProductGroup.objects.filter(resturant=self.__resturan)
        for grp in groups:
            print("Setting up priority for: %s" % grp.group_name)
            if grp.group_name in arr.keys():
                grp.priority = arr[grp.group_name]
                grp.save()
            else:
                print("Can't find")


class KfcParser:
    rest = "kfc"
    folder = "kfcdata"
    products = {}

    def __init__(self):
        self.cats = []
        self.__resturan = Resturant.objects.get(short_name=self.rest)

    def parse_main(self):
        soup = create_soup_from_file(self.folder + "/main.html")
        menu = soup.find('li', {'class': 'menu'})
        ul = menu.findChild('ul', {'class': 'sub-nav'})
        self.cats = [a['href'] for a in ul.findChildren('a')]

    def parse_cats(self):
        for cat in self.cats:
            file_adress = self.folder + cat + ".html"
            soup = create_soup_from_file(file_adress)
            h1 = soup.find('h1', {'class': 'page-title'})
            if h1 is None:
                break
            cat_name = h1.text.strip()
            self.products[cat_name] = []

            prods = soup.findChild('ul', {'class': 'products-detail-list group'})
            lis = prods.findChildren('li')
            for li in lis:
                name = li.findChild('h4').text
                if u"Пиво" in name or "Bud" in name:
                    continue
                url = li.findChild('a')['href']
                self.products[cat_name].append([name, url])

    def parse_prices(self):
        for key in self.products.keys():
            new_arr = []
            for val in self.products.get(key):
                fa = self.folder + val[1] + ".html"
                soup = create_soup_from_file(fa)
                price = soup.find('h3', {'class': 'price'}).text.strip().split()[0]
                new_arr.append([val[0], int(price)])
            self.products[key] = new_arr

    # DJANGO stuff below
    def update_django(self):
        for key in self.products.keys():
            if ProductGroup.objects.filter(group_name=key, resturant=self.__resturan).exists():
                pg = ProductGroup.objects.filter(group_name=key, resturant=self.__resturan)[0]
                print("Updating group: %s" % pg)
            else:
                pg = ProductGroup(group_name=key, resturant=self.__resturan)
                pg.save()
                print("Creating group: %s" % pg)
            prod_arr = self.products.get(key)
            for prod in prod_arr:
                if Product.objects.filter(product_name=prod[0], group=pg).exists():
                    p = Product.objects.filter(product_name=prod[0], group=pg)[0]
                    p.update(prod[1], self.rest, 0)
                else:
                    p = Product(product_name=prod[0], group=pg, price=prod[1], resturant=self.__resturan, ccal=0)
                    p.save()
            pg.save()

        self.mirror_check()

    def set_priority(self, arr):
        groups = ProductGroup.objects.filter(resturant=self.__resturan)
        for grp in groups:
            print("Setting up priority for: %s" % grp.group_name)
            if grp.group_name in arr.keys():
                grp.priority = arr[grp.group_name]
                grp.save()
            else:
                print("Can't find")

    def mirror_check(self):
        print("Starting mirror check...")
        keys_arr = self.products.keys()
        for group in ProductGroup.objects.filter(resturant=self.__resturan):
            if group.group_name not in keys_arr:
                print("Deleting redundant group: %s" % group.group_name)
                group.delete()
                continue
            prod_arr = [prod[0] for prod in self.products.get(group.group_name)]
            for product in Product.objects.filter(group=group):
                if product.product_name not in prod_arr:
                    print("Deleting redundant object: %s" % product.product_name)
                    product.delete()
