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

    # Receive message from the page
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # click on client in list of chats block
        if text_data_json.get('type') == 'get_messages':
            # get all client messages
            client_messages = await database_sync_to_async(
                Message.objects.prefetch_related('user', 'client').filter)(
                client__user__username=text_data_json.get('client_id'))

            # send each message to page
            for message in client_messages:
                author = 'from_operator'
                if message.user.client_flag == True:
                    author = 'from_client'

                await self.send_html_block('main/message.html',
                                           'message',
                                           {'message_id': message.id,
                                            'client_id': text_data_json.get('client_id'),
                                            'client_msg': True if author == 'from_client' else False,
                                            'client_name': '{} {}'.format(message.user.last_name,
                                                                          message.user.first_name),
                                            'client_profile_pic': message.client.profile_pic_url,
                                            'date': message.receive_date,
                                            'time': message.receive_time,
                                            'author': author,
                                            'message_text': message.message_text})

        # operator send message to client
        elif text_data_json.get('type') == 'send_message':
            # create message in db
            await database_sync_to_async(Message.objects.create)(
                client=Client.objects.get(user__username=text_data_json['client_id']),
                user=get_user(self),
                message_text=text_data_json['message'])

            # send message through facebook api
            send_msg_to_user(text_data_json['client_id'], text_data_json['message'])

    # Receive new client messages (from signal)
    async def message_receive(self, event):
        graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version="3.1")
        fb_user = graph.get_object(id=event.get('client_id'))
        user = await database_sync_to_async(User.objects.get)(pk=event.get('user_pk'))
        message = await database_sync_to_async(Message.objects.get)(pk=event.get('message_id'))

        author = 'from_operator'
        if user.client_flag == True:
            author = 'from_client'

        # send message to page
        await self.send_html_block('main/message.html',
                                   'message',
                                   {'message_id': message.id,
                                    'client_id': event.get('client_id'),
                                    'client_msg': True if author == 'from_client' else False,
                                    'client_name': '{} {}'.format(user.last_name, user.first_name),
                                    'client_profile_pic': fb_user.get('profile_pic'),
                                    'date': message.receive_date,
                                    'time': message.receive_time,
                                    'author': author,
                                    'message_text': message.message_text})

    # Receive new user from webhook
    async def user_receive(self, user_info):
        await self.send_html_block('main/nav_user.html',
                                   'client',
                                   user_info)
