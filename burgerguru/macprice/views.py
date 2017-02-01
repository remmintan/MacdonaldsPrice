from django.shortcuts import render
from django.views import View

# Create your views here.
class DevView(View):
	def get(self, request, sum):
		return render(request, 'macprice/index.html', { 'sum':sum })

