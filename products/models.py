from django.db import models
from users.models import Shop, User, Address, Shop
from django.core.exceptions import ValidationError


class Product(models.Model):
    slug=models.SlugField(null=False, blank=False, unique=True)
    title=models.CharField(max_length=255, null=False, blank=False)
    description=models.TextField(null=True, blank=True)
    price=models.FloatField(default=0, null=False, blank=False)
    discount=models.FloatField(default=0, null=True, blank=True)
    quantity=models.IntegerField(default=1, null=True, blank=True)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return self.slug

    @property
    def _total_price(self):
        return self.price - (self.price * (self.discount/100)) 
    @property
    def discount_amount(self):
        return self.price * (self.discount/100)


class CartProduct(models.Model):
    slug = models.SlugField(null=False, blank=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)    
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=False, blank=False)
    is_ordered = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1, null=True, blank=True)

    def __str__(self) -> str:
        return self.slug
    @property
    def _total_price(self):
        return self.product._total_price * self.quantity


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)

    def __str__(self):
        return f"{self.product}-image"

class Orders(models.Model):
    product = models.ForeignKey(CartProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    product_cost = models.FloatField()
    delivery_cost = models.FloatField(default=100)

    def __str__(self) -> str:
        return f"{self.product}-{self.ordered_at}"

    @property
    def total_cost(self):
        return self.product_cost + self.delivery_cost    