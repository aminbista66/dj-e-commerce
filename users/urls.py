from django.urls import path
from .views import (
    CreateUser,
    CreateShop,
    RegisterAsOwner,
    AddAddress,
    DeleteShop,
    DetailShop,
    ListShop,
    UpdateShop,
    RevokeAsOwner,
    AddressDetail,
    ListAddress,
    UpdateAddress,
    DeleteAddress,
    UserPublicDataView
)


app_name = "users-app"

urlpatterns = [
    path('create/', CreateUser.as_view()),
    path('detail/', UserPublicDataView.as_view()),
    path('owner/register/', RegisterAsOwner.as_view()),
    path('owner/revoke/', RevokeAsOwner.as_view()),
    path('shop/create/', CreateShop.as_view()),
    path('shop/delete/<int:pk>/', DeleteShop.as_view()),
    path('shop/list/', ListShop.as_view()),
    path('shop/detail/<int:pk>/', DetailShop.as_view()),
    path('shop/update/<int:pk>/',UpdateShop.as_view()),
    path('address/add/', AddAddress.as_view()),
    path('address/update/<int:pk>/', UpdateAddress.as_view()),
    path('address/detail/<int:pk>/', AddressDetail.as_view()),
    path('address/list/', ListAddress.as_view()),
    path('address/delete/<int:pk>/', DeleteAddress.as_view()),
]
