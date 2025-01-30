from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from panel.models import Messages, Setting, Lottery
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



# @receiver(post_save, sender=Messages)
# def update_unread_messages(sender, instance, created, **kwargs):
#     setting = Setting.objects.get(id=1)
#     if created and instance.status == 'OPEN':
#         if setting.total_unread_messages is not None:
#             setting.total_unread_messages += 1
#         else:
#             setting.total_unread_messages = 0
#         setting.save()
#     if not created and instance.status == 'CLOSED':
#         setting.total_unread_messages -= 1
#         setting.save()
#     # Broadcast the message to all connected clients
#     data = {
#         'total_unread_messages': setting.total_unread_messages,
#         'total_new_payments': setting.total_payments,
#     }
#     print('setting_values is: ', data)
#     channel_layer = get_channel_layer()
#     message = 'test unread conter with websocket protocol!'
#
#
#     channel_layer.group_send("unread", {
#         'type': 'chat_message',
#         'message': 'helowo',
#     })
#     print("done!")
#

# @receiver(post_save, sender=Lottery)
# def new_payment(sender, instance, created, **kwargs):
#     setting = Setting.objects.get(id=1)
#     status = not created and instance.status == 'Registered' and instance.payment_picture
#     print(sender, instance, created, status, instance.payment_picture)
#     # if status and instance.payment_status == 'PENDING':
#     #     if setting.total_payments is not None:
#     #         setting.total_payments += 1
#     #     else:
#     #         setting.total_payments = 0
#     #     setting.save()
#     #     print(setting.total_payments)
#     if status and instance.payment_status == 'PAID':
#         setting.total_payments -= 1
#         setting.save()