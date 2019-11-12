import asyncio
import json

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from .models import Thread, ChatMessage


class ThreadConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        thread_id = self.scope['url_route']['kwargs']['thread_id']
        me = self.scope['user']
        thread_obj = await self.get_thread(thread_id)
        self.thread_obj = thread_obj
        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        thread_messages = ChatMessage.objects.filter(thread=self.thread_obj)

        await self.send({
            "type": "websocket.accept"
        })


    async def websocket_receive(self, event):
        #when a message is received from the websocket
        print("receive", event)
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = loaded_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username
            myResponse = {
                'message': msg,
                'username': username
            }
            await self.create_chat_message(user, msg)
            # broadcast the message event to be sent
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(myResponse)
                }
            )
        # {'type': 'websocket.receive', 'text': '{"message":"abc"}'}


    async def thread_messages(self, event):
        for message in event['thread_messages']:
            await self.send({
                "type": "websocket.send",
                "text": event['text']
            })


    async def chat_message(self, event):
        # send the actual message
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })


    async def websocket_disconnect(self, event):
        #when the socket connects
        print("disconnected", event)
        await self.channel_layer.group_discard(
            self.chat_room,
            self.channel_name
        )
        raise StopConsumer()


    @database_sync_to_async
    def get_thread(self, thread_id):
        return Thread.objects.get(pk=thread_id)


    @database_sync_to_async
    def create_chat_message(self, me, msg):
        thread_obj  = self.thread_obj
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)


class UserConsumer(AsyncConsumer):

    async def websocket_connect(self, event):

        user = self.scope['user']

        threads = await self.get_user_threads(user)

        self.threads = threads

        for thread in threads:
            await self.channel_layer.group_add(
                thread.get_chat_room_name(),
                self.channel_name
            )

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):

        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = loaded_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username
            myResponse = {
                'message': msg,
                'username': username
            }
            await self.create_chat_message(user, msg)
            # broadcast the message event to be sent
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(myResponse)
                }
            )

    async def chat_message(self, event):
        # send the actual message
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):

        for thread in self.threads:
            await self.channel_layer.group_discard(
                thread.get_chat_room_name(),
                self.channel_name
            )

        raise StopConsumer()

    @database_sync_to_async
    def get_user_threads(self, user):
        return Thread.objects.filter(users=user)

    @database_sync_to_async
    def create_chat_message(self, me, msg):
        thread_obj  = self.thread_obj
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)
