from .. import models

import math

def findDesp(group, r):
		products = models.Product.objects.filter(group=group, resturant=r)
		summ = 0
		colProds = len(products)
		for product in products:
			if product.price == -1:
				colProds+=-1
			else:
				summ += (product.price - group.average_price)**2
		summ /= colProds
		summ = math.sqrt(summ)
		
		return summ

def getGroupInfo(name, rest):
	grpDict = {}
	r = models.Resturant.objects.get(short_name=rest)
	gp = models.ProductGroup.objects.get(group_name = name, resturant=r);
	grpDict['name'] = gp.group_name
	grpDict['aver'] = gp.average_price
	grpDict['all'] = models.Product.objects.filter(group=gp, resturant=r)
	
	grpDict['low'] = grpDict['all'].order_by('price')[0].price
	grpDict['high'] = grpDict['all'].order_by('-price')[0].price
	grpDict['desp'] = findDesp(gp, r)
	
	return grpDict
