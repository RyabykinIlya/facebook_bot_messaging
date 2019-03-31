import requests

from Bemeta.settings import ACCESS_TOKEN, F_API_VERSION

def send_msg_to_user(user_id, msg):
    data = {
        'recipient': {'id': user_id},
        'message': {'text': msg}
    }
    requests.post('https://graph.facebook.com/{0}/me/messages?access_token={1}'.format(F_API_VERSION, ACCESS_TOKEN),
                  json=data)