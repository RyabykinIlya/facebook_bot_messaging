from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import channels.layers
from asgiref.sync import async_to_sync

from main.models import Client, Message

@receiver(post_save, sender=Message, dispatch_uid='manage_messages')
# @receiver(pre_delete, sender=Message, dispatch_uid='manage_commands')
def manage_messages(sender, instance, **kwargs):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'fb-messages',
        {
            'type': 'group_receive',
            'message': instance.message_text,
            'user_pk': instance.user.pk,
            'client_id': instance.client.user.username
        }
    )
