import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
import jwt
from rest_framework.exceptions import AuthenticationFailed
from game.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

# Initialize Django ASGI application first
django_asgi_app = get_asgi_application()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate users via JWT in WebSocket connections.
    """
    async def __call__(self, scope, receive, send):
        from users.models import TranscendenceUser  # Import here to avoid early loading
        from django.contrib.auth.models import AnonymousUser  # Import here to avoid early loading

        # Extract the JWT token from the query string
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params.get("token", [None])[0]

        if token:
            try:
                # Decode the token
                payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=["HS256"])
                user_id = payload.get("user_id")

                # Fetch the user from the database
                user = await self.get_user(user_id)
                scope["user"] = user

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Token has expired.")
            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid token.")
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        from users.models import TranscendenceUser  # Import here to avoid early loading
        from django.contrib.auth.models import AnonymousUser  # Import here to avoid early loading
        try:
            user = await TranscendenceUser.objects.aget(id=user_id)
            return user
        except TranscendenceUser.DoesNotExist:
            return AnonymousUser()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
