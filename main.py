from bs4 import BeautifulSoup as BS

f = open('pretty.html', 'r')
soup = BS(f.read(), 'html5lib')
f.close()

#hardParcing
products = soup.find('div', {'class':'products__list'})
prodDict = {}
rowList = products.findChildren('div', {'class':'row'})
for row in rowList:
	catTitle = row.findChildren('h2', {'class':'products__cat-title'})[0]
	prodLinks = row.findChildren('a', {'class': 'products__item-link'})
	
	prodDict[catTitle.text.strip()] = [ a['title'].strip()+" - "+a['href'].strip() for a in prodLinks ]


for key in prodDict.keys():
	print("{0}: ".format(key))
	for item in prodDict.get(key):
		print("	{0}:".format(item))
		
