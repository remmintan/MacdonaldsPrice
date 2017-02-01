from __future__ import unicode_literals

from django.db import models

from decimal import Decimal

# Create your models here.
class ProductGroup(models.Model):
	group_name = models.CharField(max_length=50)
	average_price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
	
	def __unicode__(self):
		return self.group_name

class Product(models.Model):
	product_name = models.CharField(max_length=50)
	price = models.IntegerField()
	group = models.ForeignKey(ProductGroup)
	TYPE_CHOICES = [
		('N', 'Singular'),
		('S', 'Small'),
		('M', 'Medium'),
		('L', 'Large')
	]
	product_type = models.CharField(max_length = 1, choices=TYPE_CHOICES, default="N")
	
	def update(self, price):
		if self.price != price:
			self.price = price
			self.save()
	
	def __unicode__(self):
		return "{0} - {1}".format(self.product_name, self.price)
