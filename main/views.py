from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.generic import DetailView
from django.contrib.auth.models import User

import facebook
import json
import channels.layers
from asgiref.sync import async_to_sync

from Bemeta.settings import SECRET_KEY, ACCESS_TOKEN
from main.models import Client, Message, User


#    graph = facebook.GraphAPI(access_token='EAAGCNqNrl0UBABpoAzlqBuv2ZCEt6DvVoZADu6W5gTWNxMzBxPsRbFhSPXkc7u01aVtcPHdkcuePcoxCskxyDVmLuvRXqCcyHdI4NZAGfxR6WS0fx0wMQb6jc11BtisNbUiuNgnwWZCRfMANLtIQSenjvZAl5qCIv3HYqcJUoGY69h3f8F7H0',version='2.12')


def index(request):
    clients = Client.objects.all().prefetch_related('user')
    context = {
        'clients': clients,
    }
    return render(request, 'main/main.html', context)


def webhook(request):
    if (request.method == 'GET'):
        if request.GET.get('hub.mode') == 'subscribe':
            if request.GET.get('hub.verify_token') == SECRET_KEY:
                return HttpResponse(request.GET.get('hub.challenge'), status=200)
        else:
            return HttpResponse(json.dumps('Not found'), status=404)

    if (request.method == 'POST'):
        data = json.loads(request.body)
        print(data)

        try:
            if data.get('object') == 'page':
                sender_id = data.get('entry')[0].get('messaging')[0].get('sender').get('id')
                msg_block = data.get('entry')[0].get('messaging')[0].get('message')
                if msg_block.get('is_echo') is True:
                    return HttpResponse('ok', status=200)
                else:
                    user, created = User.objects.get_or_create(username=sender_id)
                    if created == True:
                        graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version='3.1')
                        fb_user = graph.get_object(id=sender_id)
                        user.last_name = fb_user.get('last_name')
                        user.first_name = fb_user.get('first_name')
                        user.client_flag = True
                        client = Client.objects.create(profile_pic_url=fb_user.get('profile_pic'),
                                                       user=user)
                        user.save()
                    else:
                        client = Client.objects.get(user__username=sender_id)
                    Message.objects.create(message_text=msg_block.get('text'),
                                           user=user,
                                           client=client)

        except (KeyError, TypeError):
            return HttpResponse('Not Found', status=404)

            # response same message back
            # try:
            #     if data.get('object') == 'page':
            #         sender = data.get('entry')[0].get('messaging')[0].get('sender').get('id')
            #         msg_block = data.get('entry')[0].get('messaging')[0].get('message')
            #
            #         if msg_block.get('is_echo') is True:
            #             pass
            #         else:
            #             pass
            #               send_msg_to_user(sender, msg_block.get('text'))
            # except (KeyError, TypeError):
            #     print('errored')
            #     return HttpResponse('ok', status=200)

    return HttpResponse('ok', status=200)
