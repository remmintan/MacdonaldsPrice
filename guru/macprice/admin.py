from django.contrib import admin

from macprice.models import ProductGroup, User, Chat, Resturant, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductGroup)
admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Resturant)
