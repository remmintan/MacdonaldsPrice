# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 17:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('macprice', '0015_user_lastsum'),
    ]

    operations = [
        migrations.AddField(
            model_name='productgroup',
            name='resturant',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='macprice.Resturant'),
        ),
    ]
