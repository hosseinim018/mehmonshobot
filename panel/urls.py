from .views import *
from .Consumers import Lottery, TotalUnRead, MessagesSocet, TotalUnReadMessage
from django.urls import path, re_path


urlpatterns = [
    path("getUsers", get_users),
    path("loadProfile", load_profile_based_on_id),
    path("recordChangesOfProfile", recordChangesOfProfile),
    path("loadProfileFriends", loadProfileFriends),
    path("sortLotteryBasedOnHighest", sortLotteryBasedOnHighest),
    path("modalHandlerLotteryProfile", modalHandlerLotteryProfile),
    path("modalHandlerLotteryWinningProfile", modalHandlerLotteryWinningProfile),
    path("modalHandlerLotteryWinning", modalHandlerLotteryWinning),
    path("loadMessagesyHistoryOfProfile", loadMessagesyHistoryOfProfile),
    path("loadMessagesyHistory", loadMessagesyHistory),
    path("loadMessagesContents", loadMessagesContents),
    path("deleteProfile", deleteProfile),
    path("deleteMessage", deleteMessage),
    path("removeAllMessageProfile", removeAllMessageProfile),
    path("closeMessage", closeMessage),
    path("addAdmin", addAdmin),
    path("getAdmins", getAdmins),
    path("removeAdmin", removeAdmin),
    path("addGame", addGame),
    path("getGames", getGames),
    path("removeGame", removeGame),
    path("setCard", setCard),
    path("updateCard", updateCard),
    path("setOrUpdateCard", set_or_update_card),
    path("getSettings", getSettings),
    path("updateChannelSettings", updateChannelSettings),
    path("sendMessage", send_message),
    path("sendMessage2", send_message2),
    path("sendMessageWithImage", sendMessageWithImage),
    path("sendMessageToWinner", sendMessageToWinner),
    path("sendMessageWithImageToWinner", sendMessageWithImageToWinner),
    path("sendTicket", sendTicket),
    path("setDate", setDate),
    path("selectToWin", selectToWin),
    path("generateExcel", generateExcel),
    path("endLottery", endLottery),
    path('totalUnReadMessagesAndNewPayment', totalUnReadMessagesAndNewPayment, name='totalUnReadMessagesAndNewPayment'),
    path('unReadMessages', unReadMessages, name='unReadMessages'),
    path('getPaymentsDate', getPaymentsDate, name='getPaymentsDate'),
    path('getPayments', getPayments, name='getPayments'),
    path('Inquiry', Inquiry, name='Inquiry'),
    path('Reverse', Reverse, name='Reverse'),
    path('sendToAll', sendToAll, name='sendToAll'),
    path('getParticipantsOFLottery', getParticipantsOFLottery, name='getParticipantsOFLottery'),
    path('getLotteryHistory', getLotteryHistory, name='getLotteryHistory'),
]

websocket_urlpatterns = [
    re_path(r'ws/lottery/', Lottery.as_asgi()),
    re_path(r'ws/totalUnRead/', TotalUnRead.as_asgi()),
    re_path(r'ws/supportMessages/', MessagesSocet.as_asgi()),
    re_path(r'ws/TotalUnReadMessage/', TotalUnReadMessage.as_asgi()),
]