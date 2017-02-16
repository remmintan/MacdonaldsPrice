from django.contrib import admin
from models import Product, ProductGroup, User, Chat, Resturant

# Register your models here.
admin.site.register(ProductGroup)
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Resturant)
