# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-07 19:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('macprice', '0011_auto_20170207_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resturant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=3)),
                ('long_name', models.CharField(max_length=30)),
            ],
        ),
    ]