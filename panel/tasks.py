from celery import shared_task
from celery.utils.log import get_task_logger
from panel.models import Lottery, LotteryHistory, Setting, Profile
from monogram.methods.sendMessage import sendMessage
# from monogram.methods import *
# from monogram import *
from monogram.text import *
from monogram.types import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import random, json
from django.conf import settings as dj_settings
from django.forms.models import model_to_dict
import datetime

logger = get_task_logger(__name__)
ALLOWED_HOSTS = dj_settings.ALLOWED_HOSTS[0] if dj_settings.ALLOWED_HOSTS else 'mybotadmin.site'

@shared_task
def sendToChannel(message):
    """
    send message befor impelement lottery
    """
    # logger.info(f"lottery is send to channenl. {message}")
    setting = Setting.objects.get(id=1)
    channdel_id = setting.channel
    sendMessage(chat_id=channdel_id, text=message)


@shared_task
def sendToAll(message):
    logger.info('send to all')
    web_app = WebAppInfo(url=f"https://{ALLOWED_HOSTS}/Lottery")
    keyboard = [
        [InlineKeyboardButton("قرعه کشی", web_app=web_app)],
    ]
    keyboard = InlineKeyboardMarkup(keyboard)
    # print(keyboard)
    lotteries = Lottery.objects.all()
    for lottery in lotteries:
        profile = lottery.profile
        chat_id = profile.user_id
        sendMessage(chat_id=chat_id, text=message, reply_markup=keyboard)


@shared_task
def lottery_before_start():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('chat', {
        'type': 'chat_message',
        'message': json.dumps({
            'status': False,
        }),
    })
    befor_lottery_channel_message = 'قرعه کشی 15 دقیقه دیگر شروع میشود, از طریق ربات برای تماشای قرعه کشی به صورت زنده استفاده کنید'
    befor_lottery_message = 'قرعه کشی 15 دقیقه دیگر شروع میشود, از دکمه زیر برای تماشای قرعه کشی به صورت زنده استفاده کنید'
    sendToChannel(befor_lottery_channel_message)
    sendToAll(befor_lottery_message)

@shared_task
def lottery_started():
    lotteries = Lottery.objects.filter(status='Registered', payment_status='PAID')
    # Get a list of all matching lotteries
    lottery_list = list(lotteries)

    # Randomly select 3 lotteries from the list

    random_lotteries = lottery_list if len(lottery_list) < 4 else random.sample(lottery_list, 3)

    random_lotteries = [model_to_dict(obj) for obj in random_lotteries]
    winners_id = []
    for l in random_lotteries:
        l['ticket_picture'] = l['ticket_picture'].url
        l['payment_picture'] = l['payment_picture'].url
        id = l['profile']
        winners_id.append(id)
        profile = Profile.objects.get(id=id)
        l['profile_picture'] = profile.picture.url if profile.picture else None
        l['enter_name'] = profile.enter_name
        l['enter_id'] = profile.enter_id
        del l['friends']
        # ll = Lottery.objects.get(pk=l['id'])
        # ll.winning = True
        # ll.save()

    lottery_history = LotteryHistory(winners=winners_id)
    lottery_history.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('chat', {
        'type': 'chat_message',
        'message': json.dumps({
            'status': True,
            'winners': random_lotteries
        }),
    })
    lottery_msg_channel = 'قرعه کشی شروع شده, از طریق ربات برای تماشای قرعه کشی به صورت زنده استفاده کنید'
    sendToChannel(lottery_msg_channel)



@shared_task
def lottery_ended():
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)('chat', {
    #     'type': 'chat_message',
    #     'message': json.dumps({
    #         'status': None,
    #     }),
    # })
    lh = LotteryHistory.objects.last()
    winners = lh.winners
    names = []
    message = 'تبریک! شما برنده این هفته قرعه کشی شده اید.'
    for id in winners:
        profile = Profile.objects.get(id=id)
        names.append(profile.enter_name)
        chat_id = profile.user_id
        sendMessage(chat_id=chat_id, text=message)
    if names:
        names = ', '.join(names)
        lottery_msg_channel = "پایان قرعه کشی, برندگان:" + "\n" + names
        sendToChannel(lottery_msg_channel)
        # sendToAll(lottery_msg_channel)

        registered_lotteries = Lottery.objects.filter(status='Registered')
        for lottery in registered_lotteries:
            lottery.status = 'Unregistered'
            lottery.save()
    else:
        sendToChannel('این هفته هیچ برنده ای نداشتیم!')