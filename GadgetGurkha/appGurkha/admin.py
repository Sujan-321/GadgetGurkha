from django.contrib import admin
from .models import *

admin.site.register([Admin, Cart, Customer, Category, Product, CartProduct, Order, ProductImage])

# Register your models here.
