# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macprice', '0020_auto_20170303_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='resturant',
            field=models.CharField(choices=[('mac', 'Макдональдс'), ('kfc', 'KFC'), ('bk', 'Бургер Кинг')], default='mac', max_length=3),
        ),
    ]
