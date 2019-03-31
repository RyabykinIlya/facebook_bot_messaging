from django.shortcuts import render

import json
import facebook
from channels.db import database_sync_to_async

from main.classes_override import AsyncWebsocketConsumerCustom
from main.facebook_helpers import send_msg_to_user
from main.models import Client, Message, User
from Bemeta.settings import ACCESS_TOKEN
from main.helpers import get_user


class AsyncMessageReceiver(AsyncWebsocketConsumerCustom):
    async def connect(self):
        # create connection to server once
        await self.channel_layer.group_add('fb-messages', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print('Received from page: {}'.format(text_data_json))
        if text_data_json.get('type') == 'get_messages':
            client_messages = await database_sync_to_async(
                Message.objects.prefetch_related('user').filter)(client__user__username=text_data_json.get('client_id'))
            for message in client_messages:
                author = 'from_operator'
                if message.user.client_flag == True:
                    author = 'from_client'

                await self.send_html_block('main/message.html',
                                           {'client_msg': True if author == 'from_client' else False,
                                            'client_profile_pic': message.client.profile_pic_url,
                                            'author': author,
                                            'message_text': message.message_text})

        elif text_data_json.get('type') == 'send_message':
            await database_sync_to_async(Message.objects.create)(
                client=Client.objects.get(user__username=text_data_json['client_id']),
                user=get_user(self),
                message_text=text_data_json['message'])

            send_msg_to_user(text_data_json['client_id'], text_data_json['message'])

    # Receive message from group
    async def group_receive(self, event):
        print('receiving from group', event)
        # message = event['message']
        graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version="3.1")
        usr = graph.get_object(id=event.get('client_id'))
        user = await database_sync_to_async(User.objects.get)(pk=event.get('user_pk'))
        author = 'from_operator'
        if user.client_flag == True:
            author = 'from_client'

        await self.send_html_block('main/message.html',
                                   {'client_msg': True if author == 'from_client' else False,
                                    'client_profile_pic': usr.get('profile_pic'),
                                    'author': author,
                                    'message_text': event.get('message')})
