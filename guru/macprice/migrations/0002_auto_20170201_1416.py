# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-01 14:16
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('macprice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('N', 'Singular'), ('S', 'Small'), ('M', 'Medium'), ('L', 'Large')],
                                   default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='productgroup',
            name='average_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5),
        ),
    ]
