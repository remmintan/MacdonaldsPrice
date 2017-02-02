# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views import View

from models import ProductGroup, Product

# Create your views here.
class DevView(View):
	def get(self, request, sum):
		groups = ProductGroup.objects.filter(average_price__lte = sum)
		sumList = ["%s - %d" %(group.group_name, group.average_price) for group in groups]
		products = Product.objects.filter(group=ProductGroup.objects.filter(group_name="Сандвичи"), price__lte = float(sum)*0.8, product_type="N")
		return render(request, 'macprice/index.html', { 'sumList':sumList, 'prodList':products })
