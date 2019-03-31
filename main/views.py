from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError

import facebook
import json

from Bemeta.settings import SECRET_KEY, ACCESS_TOKEN
from main.models import Client, Message, User
from main.helpers import send_new_user_to_group

def index(request):
    clients = Client.objects.all().prefetch_related('user')
    context = {
        'clients': clients,
    }
    return render(request, 'main/main.html', context)


def webhook(request):
    '''
    accepting facebook app verification
    during facebook app setup you have to specify:
        - safety marker IS value of SECRET_KEY from settings.py
        - webhook url IS this app url appended with /webhook, like 'https://79241062.ngrok.io/webhook'
    '''
    if (request.method == 'GET'):
        if request.GET.get('hub.mode') == 'subscribe':
            if request.GET.get('hub.verify_token') == SECRET_KEY:
                return HttpResponse(request.GET.get('hub.challenge'), status=200)
        else:
            return HttpResponse(json.dumps('Not found'), status=404)

    # facebook webhook receiver
    if (request.method == 'POST'):
        data = json.loads(request.body)

        try:
            if data.get('object') == 'page':
                sender_id = data.get('entry')[0].get('messaging')[0].get('sender').get('id')
                msg_block = data.get('entry')[0].get('messaging')[0].get('message')

                # if message sent by operator
                if msg_block.get('is_echo') is True:
                    return HttpResponse('ok', status=200)
                else:
                    # create client if not exist
                    user, created = User.objects.get_or_create(username=sender_id)
                    if created == True:
                        # if new client created - get info about him and write to database
                        graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version='3.1')
                        fb_user = graph.get_object(id=sender_id)
                        user.last_name = fb_user.get('last_name')
                        user.first_name = fb_user.get('first_name')
                        user.client_flag = True
                        client = Client.objects.create(profile_pic_url=fb_user.get('profile_pic'),
                                                       user=user)
                        user.save()
                        send_new_user_to_group(user.username, user.last_name, user.first_name, client.profile_pic_url)
                    else:
                        client = Client.objects.get(user__username=sender_id)
                    Message.objects.create(message_text=msg_block.get('text'),
                                           user=user,
                                           client=client)

        except (KeyError, TypeError, IntegrityError):
            # happen if not messages event will come or message is empty
            # send code 200 because if 404 then fb will now send new messages
            return HttpResponse('Not Found', status=200)

    return HttpResponse('ok', status=200)
