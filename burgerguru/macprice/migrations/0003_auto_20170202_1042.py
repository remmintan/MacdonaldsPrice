# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-02 10:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macprice', '0002_auto_20170201_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productgroup',
            name='average_price',
            field=models.IntegerField(default=0),
        ),
    ]
