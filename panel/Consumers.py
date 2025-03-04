import datetime
# from panel.models import Setting, Lottery, Setting
from panel.models import Lottery as LotteryModel, Setting, Profile, LotteryHistory
# from assist import get_date_in_current_week
from monogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import QuerySet
from panel.tasks import sendToAll
import logging

logger = logging.getLogger(__name__)

class Lottery(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add('chat', self.channel_name)
            self.connected_users.add(self.channel_name)
            await self.send_user_count()
        except ConnectionError as e:
            logger.error(f"Lottery connection error: {e}")
            await self.close()

    async def sendGroup(self, data=None):
        """
        This asynchronous method sends a message to a group named 'chat' using the channel layer.
        The message is serialized into JSON format before being sent. The 'data' parameter can be used
        to pass additional information, although it is not utilized in the current implementation.

        """

        await self.channel_layer.group_send('chat', {
            'type': 'chat_message',
            'message': json.dumps(data),
        })

    async def chat_message(self, event):
        # Extract the message from the event
        message = event['message']

        # Send the message back to the client
        await self.send(text_data=json.dumps({'message': message}))

        # Print the message for logging/debugging purposes
        print(f'lottery chat message have new message event: {message}')

    async def disconnect(self, close_code):
        self.connected_users.remove(self.channel_name)
        await self.channel_layer.group_discard('chat', self.channel_name)
        await self.send_user_count()

    async def send_user_count(self):
        user_count = len(self.connected_users)
        await self.channel_layer.group_send('chat', {
            'type': 'chat_message',
            'message': json.dumps({'connected_users': user_count}),
        })

class TotalUnRead(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add('unread', self.channel_name)
        except ConnectionError as e:
            logger.error(f"TotalUnRead connection error: {e}")
            await self.close()

    async def chat_message(self, event):
        # Extract the message from the event
        message = event['message']

        # Send the message back to the client
        await self.send(text_data=json.dumps({'message': message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('unread', self.channel_name)

class MessagesSocet(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add('supportMessages', self.channel_name)
        except ConnectionError as e:
            logger.error(f"MessagesSocet connection error: {e}")
            await self.close()

    async def chat_message(self, event):
        # Extract the message from the event
        message = event['message']

        # Send the message back to the client
        await self.send(text_data=json.dumps({'message': message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('Messages', self.channel_name)

class TotalUnReadMessage(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            await self.channel_layer.group_add('unreadmessage', self.channel_name)
        except ConnectionError as e:
            logger.error(f"TotalUnReadMessage connection error: {e}")
            await self.close()

    async def chat_message(self, event):
        # Extract the message from the event
        message = event['message']

        # Send the message back to the client
        await self.send(text_data=json.dumps({'message': message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('unread', self.channel_name)


