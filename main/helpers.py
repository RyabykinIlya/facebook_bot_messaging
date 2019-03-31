import channels.layers
from asgiref.sync import async_to_sync

def get_user(object):
    # function returns model-referenced User-object

    if hasattr(object, 'scope'):
        if 'user' in getattr(object, 'scope'):
            return getattr(object, 'scope').get('user')
    else:
        raise TypeError('Can not return user from object {}'.format(type(object)))

def send_new_user_to_group(client_id, client_last_name, client_first_name, client_profile_pic_url):
    # function send new client info to websocket consumer

    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'fb-messages',
        {
            'type': 'user_receive',
            'client_id': client_id,
            'client_last_name': client_last_name,
            'client_first_name': client_first_name,
            'client_profile_pic_url': client_profile_pic_url
        }
    )