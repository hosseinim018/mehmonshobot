from django.http import HttpResponse
from monogram.UpdatingMessages import Update
from monogram.types import CallbackQuery
import json
from pprint import pprint
from panel.models import Setting, Profile
from monogram.methods import getChatMember
from monogram.types import ChatMember, InlineKeyboardMarkup, InlineKeyboardButton
from monogram.extentions.conversation import Conversation
import re


def is_command(message):
  try:
      # print('msggggg:', message.photo, message.text)
      text = message.text or message.caption
      if text:
          patterns = ['^/start', '📢 مشاهده کانال', '📤 ارسال لینک دعوت', '👤 ویرایش اطلاعات', '👥 لیست دوستان', '🤖 آموزش ربات', '☎ پشتیبانی', '🎟 قرعه‌کشی', '📊 آمار و ارقام', '📚 اطلاعات قرعه کشی', '/invite']
          for pattern in patterns:
              match = re.match(pattern, message.text)
              # print('match is:',pattern,message.text, match, bool(match))
              if match:
                  return True
          return False

      else:
          return False
  except AttributeError as e:
    print(f"Error accessing message attributes: {e}")
    return False

def check_regester(message):
    setting = Setting.objects.get(id=1)
    channel = setting.channel
    chat_member = getChatMember(chat_id=channel, user_id=message.chat.id)
    print(chat_member)
    if 'result' in chat_member:
        chat_member = chat_member['result']
        status = chat_member['status']
        if status != 'member' and status != 'creator' and status != 'administrator':
            channel = channel.replace('@', '')
            url = 'https://t.me/' + channel
            keyboard = [[InlineKeyboardButton("🔗 کانال", url)]]
            keyboard = InlineKeyboardMarkup(keyboard)
            message.answer("برای استفاده از ربات  ابتدا باید عضو کانال ما شوید. پس از عضو شدن مجدد از دستور /start را وارد کنید.", keyboard=keyboard)
            return False
        else:
            text = 'شما هنوز ثبت نام نکردید, برای ثبت نام از دستور /start استفاده کنید.'
            conv = Conversation(message.chat.id)
            data = conv.data()
            regestering = data['callback_data'] == 'login' or data['callback_data'] == 'enter_name' or data['callback_data'] == 'enter_id' if data else None
            # print(data, regestering)

            try:
                user = Profile.objects.get(user_id=message.chat.id)
                if user.status != 'Registered':
                    # print('state 1:UNRegistered', regestering, is_command(message))
                    if regestering and (is_command(message)):
                        # print('state 1:regestering')
                        user_info = Profile.objects.get(user_id=message.chat.id)
                        if user_info.enter_name == None:
                            c = Conversation(user_id=message.chat.id)
                            c.create(callback_data='enter_name')
                            text = '👤 نام و نام خانوادگی خود را به حروف فارسی وارد کنید, توجه داشته باشید که این نام باید مطابق با نام و نام خانوادگی درج شده روی کارت بانکی شما باشد:'
                            message.answer(text)
                        if user_info.enter_name != None and user_info.enter_id == None:
                            c = Conversation(user_id=message.chat.id)
                            c.create(callback_data='enter_id')
                            text = '🔹 لطفا یک یوزرنیم به حروف انگلیسی برای خودتان انتخاب و ارسال کنید:'
                            message.answer(text)
                        return False
                    else:
                        return True
                else:
                    return True
            except Profile.DoesNotExist:
                print('state 2', regestering, message.text == r'^/start')
                if regestering or '/start' in message.text:
                    return True
                else:
                    return False


def UpdateHandler(request, UPDATE_HANDLER):
    if request.method == 'POST' and UPDATE_HANDLER is not None:
        result = json.loads(request.body.decode('utf-8'))
        # pprint(result)
        # if 'callback_query' in result:
        #     # run callback query functions
        #     for cqf in UPDATE_HANDLER['callback_query']:
        #         # result['from_user'] = result['callback_query']
        #         # cqf(CallbackQuery(result['callback_query']))
        #         cqf(result['callback_query'])
        # else:
        update = Update(**result)
        if 'callback_query' in result:
            for cqf in UPDATE_HANDLER['callback_query']:
                cqf(update.callback_query)
        elif 'message' in result:
            # print('check regester', check_regester(update.message))
            if check_regester(update.message):
                for message in UPDATE_HANDLER['message']:
                    message(update.message)
        else:
            pass
        return HttpResponse("Hello, world!")
