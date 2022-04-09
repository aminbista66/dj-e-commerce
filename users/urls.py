from django.urls import path
from .views import (
    CreateUser,
    CreateShop,
    RegisterAsOwner,
)

from .views import TestView

app_name = "users-app"

urlpatterns = [
    path('create/', CreateUser.as_view()),
    path('owner/register/', RegisterAsOwner.as_view()),
    path('shop/create/', CreateShop.as_view()),

    path('test/', TestView.as_view())
]