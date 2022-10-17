from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'office', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')


@admin.register(SellProduct)
class SellProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sack', 'quantity', 'sell_price', 'token_number')
    list_filter = ('is_active', 'date_added')
    date_hierarchy = 'date_added'


@admin.register(PurchaseProduct)
class PurchaseProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'quantity', 'chalan_number', 'supplier')
    list_filter = ('is_active', 'date_added')
    date_hierarchy = 'date_added'


admin.site.register(Office)
admin.site.register(Stock)
admin.site.register(Supplier)
admin.site.register(LoginExpire)