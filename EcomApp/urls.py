from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products-api/',views.ProductList.as_view(),name='product-list-api'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]