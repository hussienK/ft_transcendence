from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/matchmaking/$', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'ws/updates/$', consumers.UpdatesConsumer.as_asgi()),
    re_path(r'ws/game/(?P<room_name>\w+)/$', consumers.PongGameConsumer.as_asgi()),
]