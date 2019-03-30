from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# import facebook
import json
import requests

from Bemeta.settings import SECRET_KEY, ACCESS_TOKEN, F_API_VERSION


#    graph = facebook.GraphAPI(access_token='EAAGCNqNrl0UBABpoAzlqBuv2ZCEt6DvVoZADu6W5gTWNxMzBxPsRbFhSPXkc7u01aVtcPHdkcuePcoxCskxyDVmLuvRXqCcyHdI4NZAGfxR6WS0fx0wMQb6jc11BtisNbUiuNgnwWZCRfMANLtIQSenjvZAl5qCIv3HYqcJUoGY69h3f8F7H0',version='2.12')

def index(request):
    return render(request, 'main/main.html') \

def webhook(request):
    def send_msg_to_user(user_id, msg):
        data = {
            'recipient': {'id': user_id},
            'message': {'text': msg}
        }
        requests.post('https://graph.facebook.com/{0}/me/messages?access_token={1}'.format(F_API_VERSION, ACCESS_TOKEN),
                      json=data)

    if (request.method == 'GET'):
        if request.GET.get('hub.mode') == 'subscribe':
            if request.GET.get('hub.verify_token') == SECRET_KEY:
                return HttpResponse(request.GET.get('hub.challenge'), status=200)
        else:
            return HttpResponse(json.dumps('Not found'), status=404)

    if (request.method == 'POST'):
        data = json.loads(request.body)
        if data.get('object') == 'page':
            try:
                sender = data.get('entry')[0].get('messaging')[0].get('sender').get('id')
                msg_block = data.get('entry')[0].get('messaging')[0].get('message')

                if msg_block.get('is_echo') is True:
                    pass
                else:
                    send_msg_to_user(sender, msg_block.get('text'))
            except KeyError:
                return HttpResponse(json.dumps('ok'), status=200)

    return HttpResponse(json.dumps('ok'), status=200)
