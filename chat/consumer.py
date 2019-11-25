import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from .models import Thread, ChatMessage, UserChannel


class UserConsumer(AsyncConsumer):

    @database_sync_to_async
    def save_user_channel(self, user, channel_name):
        return UserChannel.objects.create(user=user, channel_name=channel_name)

    async def websocket_connect(self, event):

        user = await self.get_authenticated_user()

        threads = await self.get_threads_by_user(user)

        self.threads = threads

        for thread in threads:
            await self.channel_layer.group_add(
                thread.get_chat_room_name(),
                self.channel_name
            )

        await self.save_user_channel(user, self.channel_name)

        await self.send({
            "type": "websocket.accept"
        })

    async def broadcast_chat_message(self, chat_message, excluded_user=None):

        message_pack = {
            'action': 'thread_message',
            'thread_id': chat_message.thread.pk,
            'username': chat_message.user.username,
            'message' : chat_message.message,
            'timestamp': int(chat_message.timestamp.timestamp()),
        }

        if excluded_user:

            dst_users = [u for u in chat_message.thread.users.all() if u.pk != excluded_user.pk]

            channel_names = await self.get_user_channel_names(dst_users)
            for channel_name in channel_names:
                await self.channel_layer.send(
                        channel_name,
                        {
                            "type": "chat_message",
                            "text": json.dumps(message_pack)
                        }
                    )

        else:

            await self.channel_layer.group_send(
                    chat_message.thread.get_chat_room_name(),
                    {
                        "type": "chat_message",
                        "text": json.dumps(message_pack)
                    }
                )

    async def broadcast_thread_create(self, thread):

        thread_detail = {
            'action': 'thread_create',
            'id': thread.pk,
            'url': reverse('thread-messages', args=[thread.pk]),
            'name' : thread.name,
        }

        await self.channel_layer.group_send(
                thread.get_chat_room_name(),
                {
                    "type": "chat_message",
                    "text": json.dumps(thread_detail)
                }
            )

    async def action_thread_message(self, chat_messages):
        """
        chat_messages: {
                thread_id: <thread_id>,
                message: <message>,
            }
        """
        thread_id = chat_messages.get('thread_id')
        message = chat_messages.get('message')
        if not message or not thread_id:
            # TODO must not allow empty thread_id, message. Respond via socket or notify admin?
            return

        user_src = await self.get_authenticated_user()
        thread = await self.get_thread(thread_id)
        if not thread:
            # TODO thread not found. Respond via socket or notify admin?
            return

        chat_message = await self.create_chat_message(thread, user_src, message)
        await self.broadcast_chat_message(chat_message)

    @database_sync_to_async
    def get_user_channel_names(self, users, expiry=86400):
        created_since = datetime.now() - timedelta(seconds=expiry)
        qs_filter = UserChannel.objects.filter(
                user__in=users,
                created_at__gte=created_since
            )
        return list(qs_filter.values_list('channel_name', flat=True))

    async def action_thread_create(self, data):
        """
        data: {
                user_ids: <user_ids>,
                message: <message>
            }
        """

        # sanitize and validate

        dst_user_ids = data.get('user_ids')
        dst_users = await self.get_users(dst_user_ids)
        if not dst_users:
            # TODO Destination user must be specified. Respond via socket or notify admin?
            return
        src_user = await self.get_authenticated_user()

        message = data.get('message')
        if not message:
            # TODO must not allow empty message. Respond via socket or notify admin?
            return

        # subscribe all user's channels to the group, including source user

        thread, is_created = await self.get_thread_for(src_user, dst_users)
        if is_created:
            channel_names = await self.get_user_channel_names([src_user] + dst_users)
            for channel_name in channel_names:
                await self.channel_layer.group_add(
                    thread.get_chat_room_name(),
                    channel_name
                )

        chat_message = await self.create_chat_message(thread, src_user, message)
        await self.broadcast_thread_create(thread)
        await self.broadcast_chat_message(chat_message, excluded_user=src_user)

    async def websocket_receive(self, event):

        """
        When sending message to a thread:
        {
            action: 'thread_message'
            params: {
                thread_id: <thread_id>,
                message: <message>,
            }
        }

        When creating thread for multiple users:
        {
            action: 'thread_create',
            params: {
                user_ids: <user_ids>,
                message: <message>,
            }
        }

        """

        await self.get_authenticated_user()

        try:
            data_raw = event.get('text', None)
            data = json.loads(data_raw)
            action = data.get('action')
            params = data.get('params')
        except:
            return

        if action == 'thread_message':
            await self.action_thread_message(params)

        if action == 'thread_create':
            await self.action_thread_create(params)

    async def chat_message(self, event):
        # send the actual message
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    @database_sync_to_async
    async def clear_user_channel(self, channel_name):
        UserChannel.objects.filter(channel_name=channel_name).delete()
        for thread in self.threads:
            await self.channel_layer.group_discard(
                thread.get_chat_room_name(),
                self.channel_name
            )

    async def websocket_disconnect(self, event):

        await self.clear_user_channel(self.channel_name)
        raise StopConsumer()

    async def get_authenticated_user(self):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            return user
        raise StopConsumer()

    @database_sync_to_async
    def get_users(self, pk_list):
        User = get_user_model()
        users = User.objects.filter(pk__in=pk_list)

        return list(users)

    @database_sync_to_async
    def get_thread_for(self, user_owner, users):
        if len(users) == 1:
            thread, is_created = Thread.objects.get_or_new(user_owner, users[0])
        else:
            # TODO notify admin or implement
            print('[ERROR] Group chat with 2+ users is not supported')
            thread = None
            is_created = False

        return thread, is_created

    @database_sync_to_async
    def get_threads_by_user(self, user):
        return Thread.objects.filter(users=user)

    @database_sync_to_async
    def get_thread(self, thread_id):
        return Thread.objects.get(pk=thread_id)

    @database_sync_to_async
    def create_chat_message(self, thread, user, message):
        return ChatMessage.objects.create(
                thread=thread,
                user=user,
                message=message
            )
