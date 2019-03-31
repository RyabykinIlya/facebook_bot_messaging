from django.shortcuts import render

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AsyncWebsocketConsumerCustom(AsyncWebsocketConsumer):
    # Overriding WebsocketConsumer class for better functionality.
    async def send_html_block(self, template, params):
        await self.send(text_data=json.dumps({
            'message': {'type': 'message_html',
                        'html_code': render(None, 'main/message.html', params).content.decode("utf-8")}
        }))

    async def send_msg(self, type, object):
        '''
        type - info or message
        msg - any string
        '''
        await self.send(text_data=json.dumps({
            str(type): object
        }))
