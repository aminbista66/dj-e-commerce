from django.urls import path

from . import views

urlpatterns=[
    path('create/', views.CreateProducts.as_view()),
    path('list/', views.ListProduct.as_view()),
    path('details/<slug:slug>/', views.DetailProduct.as_view()),
    path('create/upload-img/<slug:slug>/', views.UploadProductImage.as_view()),
    path('delete/<slug:slug>/', views.DeleteProduct.as_view()),
    path('update/<slug:slug>/', views.UpdateProduct.as_view()),
    path('add-to-cart/<slug:slug>/', views.AddToCart.as_view()),
    path('cart/list/', views.ListCartProduct.as_view()),
    path('pre-checkout/summary/', views.PreCheckoutSummary.as_view()),
    path('order/<slug:slug>/<int:id>/', views.Order.as_view()),
    path('list-order/', views.ListOrder.as_view()),
    path('cart/decrease-quantity/<slug:slug>/', views.DecreaseQuantity.as_view()),
    path('cart/increase-quantity/<slug:slug>/', views.IncreaseQuantity.as_view()),
    path('cart/delete/<slug:slug>/', views.DeleteCartProduct.as_view()),
    path('test/', views.test)
]