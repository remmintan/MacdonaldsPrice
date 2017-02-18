# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from decimal import Decimal

# Create your models here.
class Resturant(models.Model):
	short_name = models.CharField(max_length=3)
	long_name = models.CharField(max_length=30)
	
	def __unicode__(self):
		return self.long_name

class ProductGroup(models.Model):
	group_name = models.CharField(max_length=50)
	priority = models.IntegerField(default=10)#default rating is really low
	resturant = models.ForeignKey(Resturant)
	
	def __unicode__(self):
		return self.group_name

class Product(models.Model):
	product_name = models.CharField(max_length=50)
	price = models.IntegerField()
	ccal = models.IntegerField(default = 0)
	group = models.ForeignKey(ProductGroup)
	TYPE_CHOICES = [
		('N', 'Singular'),
		('S', 'Small'),
		('M', 'Medium'),
		('L', 'Large')
	]
	product_type = models.CharField(max_length = 1, choices=TYPE_CHOICES, default="N")
	resturant = models.ForeignKey(Resturant, default=None)
	
	def update(self, price, restName, ccals):
		self.price = price
		rest = Resturant.objects.filter(short_name = restName)[0]
		self.resturant = rest
		self.ccal = ccals
		self.save()
	
	def __unicode__(self):
		if self.product_type == "N":
			return "{0} - {1} ({2})".format(self.product_name, self.price, self.ccal)
		else:
			return "{0} {2} - {1} ({3})".format(self.product_name, self.price, self.product_type, self.ccal)

class User(models.Model):
	name = models.CharField(max_length=50)
	surname = models.CharField(max_length=50)
	RESTURANT_CHOICES = [
		('mac', u'Макдональдс'),
		('kfc', 'KFC'),
	]
	resturant = models.CharField(max_length=3, choices = RESTURANT_CHOICES, default="mac")
	haveChosen = models.BooleanField(default=False)
	lastSum = models.IntegerField(default = 0)
	
	def update(self, name, surname):
		if self.name != name:
			self.name = name;
			self.save()
		if self.surname != surname:
			self.surname = surname;
			self.save()
	
	def __unicode__(self):
		return "%s %s - %i" % (self.name, self.surname, self.pk)
	
class Chat(models.Model):
	chatType = models.CharField(max_length=10)
	requests = models.IntegerField(default=0)
	
	def __unicode__(self):
		
		if self.chatType == "private":
			user = User.objects.filter(pk = self.pk)[0]
			return "%s %s - %i" % (user.name, user.surname, self.requests)
		else:
			return "%i (%s) - %i" % (self.pk, self.chatType, self.requests)
