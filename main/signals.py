from django.db.models.signals import post_save
from django.dispatch import receiver

import channels.layers
from asgiref.sync import async_to_sync

from main.models import Message

@receiver(post_save, sender=Message, dispatch_uid='manage_messages')
def manage_messages(sender, instance, **kwargs):
    # signal send new message info to consumer
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'fb-messages',
        {
            'type': 'message_receive',
            'message_id': instance.id,
            'user_pk': instance.user.pk,
            'client_id': instance.client.user.username
        }
    )
