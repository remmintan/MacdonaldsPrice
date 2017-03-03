from django.shortcuts import render
from django.views import View

from guru.dev.controllers import getGroupInfo, getGroupsForRest
from guru.macprice.controllers import createOrder


# Create your views here.
def index(request):
    d = getGroupsForRest()
    print(d)
    return render(request, 'dev/index.html', {'rests': d})


class GroupView(View):
    def get(self, request, rest, name):
        d = getGroupInfo(name, rest)
        return render(request, 'dev/group.html', d)


class DevView(View):
    def get(self, request, rest, summa):
        var = createOrder(summa, rest)
        var = var.split('\n')
        return render(request, 'dev/prods.html', {'var': var})
