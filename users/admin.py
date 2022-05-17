from django.contrib import admin
from .models import User, Shop, Address

class UserList(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
    )

admin.site.register(User, UserList)


class ShopList(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'shop_name',
        'shop_location',
    )

admin.site.register(Shop, ShopList)

class AddressList(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'city',
        'area',
        'postal_code',
        'zip_code',
    )


admin.site.register(Address, AddressList)