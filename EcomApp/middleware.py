from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTWebSocketMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.jwt_authentication = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        scope["user"] = await self.get_user(scope)
        return await self.inner(scope, receive, send)

    async def get_user(self, scope):
        token = self.get_token_from_cookies(scope) or self.get_token_from_query_string(scope)
        if not token:
            return AnonymousUser()

        try:
            validated_token = self.jwt_authentication.get_validated_token(token)
            return await database_sync_to_async(self.jwt_authentication.get_user)(validated_token)
        except (InvalidToken, TokenError, Exception):
            return AnonymousUser()

    def get_token_from_cookies(self, scope):
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie")
        if not cookie_header:
            return None

        cookies = {}
        for part in cookie_header.decode().split(";"):
            if "=" in part:
                key, value = part.strip().split("=", 1)
                cookies[key] = value

        return cookies.get("jwt_access_token")

    def get_token_from_query_string(self, scope):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")
        if token_list:
            return token_list[0]
        return None


def JWTAuthMiddlewareStack(inner):
    return JWTWebSocketMiddleware(inner)