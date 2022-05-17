from rest_framework import serializers
from ..models import Orders
from users.models import Address

class OrderSerializer(serializers.ModelSerializer):
	product_name = serializers.SerializerMethodField(source='product.title', read_only=True)
	total_price = serializers.SerializerMethodField(read_only=True)
	order_status = serializers.SerializerMethodField(read_only=True)
	shop_name = serializers.SerializerMethodField(read_only=True, source='shop.shop_name')
	address = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = Orders
		fields = (
			'id',
			'product_name',
			'total_price',
			'quantity',
			'order_status',
			'ordered_at',
			'shop_name',
			'address'
			)
	def get_total_price(self, obj):
		return obj.total_cost
	def get_order_status(self, obj):
		if obj.is_delivered:
			return "delivered"
		return "pending"

	def get_address(self, obj):
		x = Address.objects.filter(user__id=obj.user.id).values()
		return x
	def get_product_name(self, obj):
		return obj.product.title
	def get_shop_name(self, obj):
		return obj.shop.shop_name