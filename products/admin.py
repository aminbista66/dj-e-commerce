from django.contrib import admin
from .models import Product, CartProduct, ProductImage, Orders


class CartProductAdminList(admin.ModelAdmin):
    list_display = (
        'slug',
        '_total_price',
        'quantity',
    )

class ProductAdminList(admin.ModelAdmin):
    list_display = (
        'slug',
        'title',
        'discount',
        'price',
        'quantity',
        '_total_price',
    )



admin.site.register(Product, ProductAdminList)
admin.site.register(CartProduct, CartProductAdminList)
admin.site.register(ProductImage)
admin.site.register(Orders)