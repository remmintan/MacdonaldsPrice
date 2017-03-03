import math
import numpy

from guru.macprice import models
from guru.macprice.controllers import Order


def findDesp(group, r):
    products = models.Product.objects.filter(group=group, resturant=r)
    summ = 0
    colProds = len(products)
    for product in products:
        if product.price == -1:
            colProds += -1
        else:
            summ += (product.price - group.average_price) ** 2
    summ /= colProds
    summ = math.sqrt(summ)

    return summ


def getGroupInfo(name, rest):
    grpDict = {}
    r = models.Resturant.objects.get(short_name=rest)
    gp = models.ProductGroup.objects.get(group_name=name, resturant=r)
    grpDict['name'] = gp.group_name

    grpDict['all'] = models.Product.objects.filter(group=gp, resturant=r, price__gte=0).order_by('price')
    prodPrices = [p.price for p in grpDict['all']]

    grpDict['med'] = int(numpy.median(prodPrices))
    grpDict['aver'] = int(numpy.mean(prodPrices))
    grpDict['low'] = int(numpy.min(prodPrices))
    grpDict['high'] = int(numpy.max(prodPrices))
    grpDict['desp'] = int(numpy.std(prodPrices))
    grpDict['tret'] = (int(numpy.percentile(prodPrices, 34)), int(numpy.percentile(prodPrices, 67)))

    grpDict['ranges'] = []
    grpDict['prodrang'] = []
    order = Order(100, r)
    for i in range(1, 4):
        rang = order.getRangeForGroup(gp, i)
        grpDict['ranges'].append([rang, i])
        grpDict['prodrang'].append([models.Product.objects.filter(group=gp, resturant=r, price__gte=rang[0],
                                                                  price__lte=rang[1]).order_by('price'), i])
    return grpDict


def getGroupsForRest():
    rests = models.Resturant.objects.all()
    rd = []
    for r in rests:
        rd.append([r.short_name, r.long_name,
                   models.ProductGroup.objects.filter(resturant=r, priority__lte=9).order_by('priority')])

    return rd
