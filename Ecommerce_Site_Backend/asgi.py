"""
ASGI config for Ecommerce_Site_Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from EcomApp.routing import websocket_urlpatterns
from EcomApp.middleware import JWTAuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecommerce_Site_Backend.settings.production')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
