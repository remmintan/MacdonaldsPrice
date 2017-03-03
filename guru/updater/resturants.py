# -*- coding: utf-8 -*-

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "guru.settings"

import django

django.setup()

from macprice.models import Resturant


def updateResturant(long_name, short_name):
    if not Resturant.objects.filter(short_name=short_name).exists():
        rest = Resturant(short_name=short_name, long_name=long_name)
        rest.save()
    else:
        rest = Resturant.objects.filter(short_name=short_name)[0]
        if rest.long_name != long_name:
            rest.long_name = long_name
            rest.save()


def updateAll():
    updateResturant(u"Макдональдс", "mac")
    updateResturant("KFC", "kfc")
