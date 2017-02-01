import django
django.setup()

from macprice.models import Product, ProductGroup
from bs4 import BeautifulSoup as BS
import time;

def getPriceForLink(link):
	pf = open('updater'+link+'.html', 'r')
	psoup = BS(pf.read(), 'html5lib')
	pf.close()
	price = psoup.find_all('h4', {'class':'product__show-price'})[0].text.strip()[:6].split(' ')[0];
	#try not load cpu
	time.sleep(1)
	return price;

f = open('updater/pretty.html', 'r')
soup = BS(f.read(), 'html5lib')
f.close()

#hardParcing
products = soup.find('div', {'class':'products__list'})
prodDict = {}
rowList = products.findChildren('div', {'class':'row'})
for row in rowList:
	catTitle = row.findChildren('h2', {'class':'products__cat-title'})[0]
	prodLinks = row.findChildren('a', {'class': 'products__item-link'})
	prodDict[catTitle.text.strip()] = []
	for a in prodLinks:
		price = getPriceForLink(a['href'].strip())
		print price
		prodDict[catTitle.text.strip()].append( [a['title'].strip(), price] )


for key in prodDict.keys():
	if not ProductGroup.objects.filter(group_name=key).exists():
		pg = ProductGroup(group_name=key)
		pg.save()
		print "Created group: " + key
	else:
		pg = ProductGroup.objects.filter(group_name=key)[0]
	
	for item in prodDict.get(key):
		if not Product.objects.filter(product_name=item[0]).exists():
			p = Product(product_name = item[0], price=0, group=pg)
			p.save()
			print "Created product: "+item[0]
		
