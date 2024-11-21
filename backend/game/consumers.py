import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class PongGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get room name from url route
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        # add the user to the game room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #remove the user from the game room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )