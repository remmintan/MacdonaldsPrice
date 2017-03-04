# -*- coding: utf-8 -*-

import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "guru.settings"
django.setup()

from macprice.models import Resturant


def update_resturant(long_name, short_name):
    if not Resturant.objects.filter(short_name=short_name).exists():
        rest = Resturant(short_name=short_name, long_name=long_name)
        rest.save()
    else:
        rest = Resturant.objects.filter(short_name=short_name)[0]
        if rest.long_name != long_name:
            rest.long_name = long_name
            rest.save()


def update_all():
    update_resturant(u"Макдональдс", "mac")
    update_resturant("KFC", "kfc")
    update_resturant(u"Бургер Кинг", "bk")
