from django.urls import path
from django.contrib.auth.models import User
from .views import *

urlpatterns = [
    path('home/',home, name='home'),
    path('products-api/',ProductList.as_view(),name='product-list-api'),
    path('user_register/', UserRegistrationView.as_view(), name='user-registration'),
    path('user_login/', UserLoginView.as_view(), name='user-login'),
    path('user_logout/', UserLogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/<int:user_id>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('order/', OrderView.as_view(), name='place-order'),
    path('order/<uuid:order_id>/item/<uuid:product_id>/',OrderDetailView.as_view(), name='order-details'),
    path('cart/', CartView.as_view(), name='cart-add-or-update'),
    path('wishlist/', WishlistView.as_view(), name='wishlist-add-or-remove'),
    path('review/', ReviewView.as_view(), name='add-review'),
    path("chat/",ChatRoomView.as_view(),name="chat-room"),
    path("store/",storeview,name="store-view"),
]