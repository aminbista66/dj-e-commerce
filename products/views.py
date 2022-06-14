
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import F, Q, Sum
import random
from products.models import Product
from users.get_user import get_user
from .helpers import generate_pdf
from .serializers.product_serializer import ProductSerializer, ProductImageUploadSerializer
from .serializers.cart_serializer import CartReadSerializer, CartSummarySerializer, CartWriteSerializer
from .serializers.order_serializer import OrderSerializer
from users.models import Address, Shop, User
from .models import CartProduct, ProductImage, Orders
from django.http import FileResponse
from django.conf import settings


class ListProduct(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_class = [permissions.AllowAny]
    queryset = Product.objects.all()


class DetailProduct(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_class = [permissions.AllowAny]
    queryset = Product.objects.all()
    lookup_field = 'slug'


class CreateProducts(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_class = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = get_user(request)
            if user_id == 0:
                return Response({"message": "user not found or token missing."})
            user = User.objects.get(id=user_id)
            if not user.is_owner:
                return Response({"message": "you are not registerd as a owner."})
            shop_data = serializer.validated_data.pop('shop')
            shop_name = shop_data['shop_name']
            shop = Shop.objects.get(shop_name=shop_name)
            if not shop.owner.id == user_id:
                return Response({"message": "sorry you are not the owner of this shop"})
            if not shop:
                return Response({"message": "No shop by this name."})
            serializer.save(shop=shop)

            return Response(serializer.data)
        return super().create(request, *args, **kwargs)


class UploadProductImage(generics.GenericAPIView):
    serializer_class = ProductImageUploadSerializer
    parser_class = [MultiPartParser, FormParser]
    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        product = Product.objects.get(slug=slug)
        if not product.exists():
            return Response({"message": "no product by this name."})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = get_user(request)
            if user_id == 0:
                return Response({"message": "user not found or token missing."})
            user = User.objects.get(id=user_id)
            print(product.shop.owner, user)
            if not user.is_owner:
                return Response({"message": "you are not registerd as a owner."})
            if product.shop.owner != user:
                return Response({"message": "you are not the owner of this product."})
            images = serializer.validated_data['images']
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            return Response(serializer.data, status=200)
        return Response(serializer.data, status=500)


class DeleteProduct(generics.DestroyAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.shop.owner.id == get_user(request):
            self.perform_destroy(instance)
            return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)
        return Response({'message': 'you dont own the product.'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class UpdateProduct(generics.UpdateAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.all()

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        if get_user(self.request) != product.shop.owner.id:
            return Response({"message": "You dont own the product."}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        return super().update(request, *args, **kwargs)


class AddToCart(generics.GenericAPIView):
    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = get_user(request)
        if user_id == 0:
            return Response({"message": "user not found"}, status=404)

        user = User.objects.get(id=user_id)

        

        product = Product.objects.filter(slug=kwargs.get('slug'))
        print(request.data.get('quantity'))

        if product.exists():
            if product.first().quantity == 0:
                return Response({"message": "Product Out Of Stock"}, status=300) 
            existing_product = CartProduct.objects.filter(
                Q(user=user) & Q(product__slug=kwargs.get('slug')))
            print(existing_product)
            if int(product.first().quantity) < int(request.data.get('quantity')):
                return Response({"message": "not enough in stock"})
            if existing_product.exists():
                existing_product_ = existing_product.first()
                if int(existing_product_.quantity) + int(request.data.get('quantity')) > int(product.first().quantity):
                    return Response({'message': 'not enough in stock'})
                existing_product_.quantity = F('quantity') + request.data.get('quantity')
                existing_product_.save()
                return Response({"message": f"total quantity {existing_product.first().quantity}", "quantity": f'{existing_product.first().quantity}'})


            cart_product = CartProduct.objects.create(
                slug=f'crt-{product.first().slug}-{random.randint(1,9999)}',
                product=product.first(),
                user=User.objects.get(id=get_user(request)),
                shop=product.first().shop,
                quantity=request.data.get('quantity')
            )

            return Response({"message": "Product Successfully Added To Cart"}, status=status.HTTP_200_OK)

class DeleteCartProduct(generics.DestroyAPIView):
    permission_class = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    def get_queryset(self):
        user = User.objects.get(id=get_user(self.request))
        qs = CartProduct.objects.filter(user=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message":"successfully deleted"},status=status.HTTP_204_NO_CONTENT)

class ListCartProduct(generics.ListAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = CartReadSerializer
    lookup_field = 'slug'
    queryset = CartProduct.objects.all()

    def get_queryset(self):
        qs = self.queryset.filter(user__id=get_user(self.request))
        return qs


class PreCheckoutSummary(generics.GenericAPIView):
    serializer_class = CartSummarySerializer

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(id=get_user(request))
        if not users.exists():
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        if users.exists():
            user = users.first()

        class SummaryData:
            def __init__(self, total_amount, total_quantity, total_discount_percent, total_discount_amount, net_amount):
                self.total_amount = total_amount
                self.total_quantity = total_quantity
                self.total_discount_percent = total_discount_percent
                self.total_discount_amount = total_discount_amount
                self.net_amount = net_amount
        cart_products = CartProduct.objects.filter(user=user)

        total_amount = [i.product._total_price for i in cart_products]
        total_quantity = cart_products.aggregate(Sum('quantity'))
        total_discount_amount = [
            i.product.discount_amount for i in cart_products]
        total_discount_percent = [i.product.discount for i in cart_products]
        net_amount = [i._total_price for i in cart_products]

        summaryobject = SummaryData(
            total_amount=sum(total_amount),
            total_quantity=total_quantity['quantity__sum'],
            total_discount_amount=sum(total_discount_amount),
            total_discount_percent=sum(total_discount_percent),
            net_amount=sum(net_amount),
        )

        serializer = self.get_serializer(summaryobject)
        return Response(serializer.data)


class Order(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        cart_product_slug = kwargs.get('slug')
        address = Address.objects.get(id=kwargs.get('id'))
        products = CartProduct.objects.filter(slug=cart_product_slug)
        print(cart_product_slug)
        if products.exists():
            product = products.first()
            home_product = Product.objects.get(slug=product.product.slug)
            order = Orders.objects.create(
                product=home_product,
                quantity=product.quantity,
                address=address,
                user=product.user,
                shop=product.shop,
                product_cost=product._total_price
            )
            print(product.product.quantity)
            home_product.quantity = F('quantity') - order.quantity
            home_product.save()
            products.delete()
            return Response({'message': 'order created'})


class ListOrder(generics.ListAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        print('hello')
        qs = Orders.objects.filter(user__id=get_user(self.request))
        return qs


class AddReview(generics.GenericAPIView):
    pass


class AddLike(generics.GenericAPIView):
    pass

class DecreaseQuantity(generics.GenericAPIView):
    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_product = CartProduct.objects.filter(slug=kwargs.get('slug'))
        if cart_product.exists():
            cart_product_ = CartProduct.objects.get(slug=kwargs['slug'])
            if cart_product_.quantity < int(request.data['quantity']):
                return Response({"message": "cart product quantity is less than the given quantity"})
            if cart_product_.quantity == int(request.data['quantity']):
                return Response({"message": "cant remove all the quantity, must have atleast one or remove the product"})
            cart_product_.quantity = F('quantity') - int(request.data.get('quantity'))
            cart_product_.save()
            return Response({"quantity": f'{cart_product.first().quantity}'})
        return Response({"message": "Product not Found"}, status=404)

class IncreaseQuantity(generics.GenericAPIView):
    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_product = CartProduct.objects.filter(slug=kwargs.get('slug'))
        product = Product.objects.get(slug=cart_product.first().product.slug)
        if cart_product.exists():
            cart_product_ = CartProduct.objects.get(slug=kwargs['slug'])
            if int(cart_product_.quantity) + int(request.data['quantity']) > int(product.quantity):
                return Response({"message": "not enough in stock"})
            if int(product.quantity) < int(request.data.get('quantity')):
                return Response({"message": "not enough in stock"})
            cart_product_.quantity = F('quantity') + int(request.data.get('quantity'))
            cart_product_.save()
            return Response({"quantity": f'{cart_product.first().quantity}'})
        return Response({"message": "Product not Found"}, status=404)



# invoice test
def test(request):
    orders = Orders.objects.all()
    filename, status = generate_pdf({'orders': orders})
    response = FileResponse(open(
        str(settings.BASE_DIR) + f'/media/{filename}.pdf', 'r+b'), as_attachment=True)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    return response
