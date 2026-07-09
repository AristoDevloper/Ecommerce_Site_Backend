from .consumers import ChatConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/(?P<room_id>[a-f0-9-]+)/$', ChatConsumer.as_asgi()),
]