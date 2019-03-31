from django.shortcuts import render

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AsyncWebsocketConsumerCustom(AsyncWebsocketConsumer):
    # Overriding WebsocketConsumer class for custom functionality.
    async def send_html_block(self, template, block_type, params):
        '''
        function send rendered template to page
        template - template name
        block_type - identifier of block: message or client
        params - parameters to render template
        '''
        await self.send(text_data=json.dumps({
            'message': {'type': 'message_html',
                        'client_id': params.get('client_id'),
                        'block_type': block_type,
                        'html_code': render(None, template, params).content.decode("utf-8")}
        }))
