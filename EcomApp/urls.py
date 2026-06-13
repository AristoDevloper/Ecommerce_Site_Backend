from django.urls import path
from django.contrib.auth.models import User
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('products-api/',ProductList.as_view(),name='product-list-api'),
    path('user_register/', UserRegistrationView.as_view(), name='user-registration'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]