from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<str:room_name>/', consumers.PongGameConsumer.as_asgi()),
	path('ws/matchmaking/', consumers.MatchmakingConsumer.as_asgi()),   
]
