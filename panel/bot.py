from monogram.methods import *
from monogram import *
from monogram.text import *
from monogram.types import *
from monogram.UpdatingMessages import *
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import quote
from panel.models import *
from monogram.extentions.conversation import Conversation
import re
from panel.assist import *
from panel.views import convert_date as cnv_date
from django.utils import timezone
from django.db.models import Exists, Count, Q
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.db import IntegrityError

import requests
from django.conf import settings as djagno_settings


session = requests.Session()

conf = configs(appname='panel')
bot = Monogram(**conf)



back_markup = ReplyKeyboardMarkup([[KeyboardButton('🔙 بازگشت')]], resize_keyboard=True)

main_keyboard = [
    [KeyboardButton('🎟 قرعه‌کشی')],
    [KeyboardButton('📚 اطلاعات قرعه کشی'), KeyboardButton('📤 ارسال لینک دعوت'), KeyboardButton('📢 مشاهده کانال'), ],
    [KeyboardButton('👤 ویرایش اطلاعات'), KeyboardButton('👥 لیست دوستان'), ],
    [
        KeyboardButton('☎ پشتیبانی'),
        KeyboardButton('📊 آمار و ارقام'),
        KeyboardButton('🤖 آموزش ربات'),
    ],
]

def invietfrend(message, friends_id):
    # invite link:
    try:
        profile = Profile.objects.get(user_id=message.chat.id)
        friend_profile = Profile.objects.get(id=friends_id)
        # Check if a friendship already exists between these two users
        friendship, created = profileFriend.objects.get_or_create(
            from_user=profile,
            to_user=friend_profile,
            defaults={"status": 'Pending'},
        )
        keyboard = [
            [
                InlineKeyboardButton("✅ تایید",
                                     callback_data=f"acceptFriend-{friend_profile.user_id}-nousername"),
                InlineKeyboardButton("❌ رد",
                                     callback_data=f"cancelFriend-{friend_profile.user_id}-nousername"),
            ]
        ]
        keyboard = InlineKeyboardMarkup(keyboard)
        # if created send request to user
        if created:
            # Check if friend is already in user's friend list
            text = f"شما از لینک دعوت به دوستی کاربری با نام {friend_profile.enter_name} و نام کاربری {friend_profile.enter_id} استفاده کردین.از دکمه زیر برای تایید درخواست استفاده کنید.{Bold('توجه داشته باشد بعد از تایید به لیست دوستان یکدیگر اضافه میشوید.')}"
            message.reply(text=text, keyboard=keyboard)
        # If the friendship already exists, update the status
        if not created:
            if friendship.status == 'Pending':
                text = f"کاربری با نام {friend_profile.enter_name} و نام کاربری {friend_profile.enter_id} قبلا برای شما درخواست دوستی فرسستاده! از دکمه زیر برای تایید درخواست استفاده کنید.{Bold('توجه داشته باشد بعد از تایید به لیست دوستان یکدیگر اضافه میشوید.')}"
                message.reply(text=text, keyboard=keyboard)
            if friendship.status == 'Accepted':
                text = f"در حال حاظر کاربری با نام {friend_profile.enter_name} و نام کاربری {friend_profile.enter_id} در لیست دوستان شما قرار دارد."
                message.reply(text=text)

    except Profile.DoesNotExist:
        text = 'هیچ کاربری با این نام کاربری در سیستم وجود ندارد\nیک نام کاربری دیگر را وارد کنید یا دکمه بازگشت را برای لفو عملیات بزنید.'
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
        keyboard = InlineKeyboardMarkup(keyboard)
        message.reply(text=text, keyboard=keyboard)

@bot.newMessage(pattern=r'^/start')
def start(message):
    # print('start stage ', message.text)
    p = getUserProfile(user_id=message.chat.id)
    # print(p)
    p = UserProfilePhotos(**p['result'])
    # print(p.photos[0][0]['file_id'])
    # print(len(p.photos) !=0)
    filename = None
    if len(p.photos) !=0:
        f = getFile(p.photos[0][0]['file_id'])
        file_path = f['result']['file_path']
        filename = f'{message.chat.id}.jpg'
        pic = bot.download_file(filename=filename, dir_path='media/img/profile_pictures', file_path=file_path)
        # print(filename)
    try:
        user_info = Profile.objects.get(user_id=message.chat.id)
        print('Profile Existed!')
        # invite link:
        callback_data = message.text.split()
        print(callback_data)
        if len(callback_data) > 1:
            firend_id = callback_data[1]
            invietfrend(message=message, friends_id=firend_id)
        else:
            text = 'سلام دوباره! خیلی خوشحالیم که به جمع ما برگشتی.'
            keyboard = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
            message.answer(text, keyboard=keyboard)
            if user_info.enter_name == None:
                c = Conversation(user_id=message.chat.id)
                c.create(callback_data='enter_name')
                text = '👤 نام و نام خانوادگی خود را به حروف فارسی وارد کنید, توجه داشته باشید که این نام باید مطابق با نام و نام خانوادگی درج شده روی کارت بانکی شما باشد:'
                message.answer(text)
            if user_info.enter_name != None and user_info.enter_id == None:
                c = Conversation(user_id=message.chat.id)
                c.create(callback_data='enter_id')
                text = '🔹 لطفا یک نام کاربری به حروف انگلیسی برای خودتان انتخاب و ارسال کنید:'
                message.answer(text)

    except Profile.DoesNotExist:
        print('No Profile')
        first_name = message.chat.first_name
        last_name = message.chat.last_name
        first_name = first_name if first_name else ''
        last_name = last_name if last_name else ''
        full_name = first_name + last_name
        filename = f"img/profile_pictures/{filename}" if filename else None
        username = message.chat.username
        user_id = message.chat.id
        status = 'Registering'
        print(full_name, username, user_id, filename, status)
        try:
            user_info = Profile.objects.create(
                full_name=full_name,
                username=username,
                user_id=user_id,
                picture=filename,
                status=status
            )

            print(user_info)
            welcome_message = f"""سلام رفیق گل! ‍♀️‍♂️به {Bold('ربات مهمونشو')} خوش اومدی! اینجا یه جای باحالِ پر از آدمای باحالِ خوش‌گذرانِ دوست‌داشتنیه! هر هفته یه {Bold('قرعه‌کشی خفن')} داریم که برنده‌ها باید با جایزه‌شون دوستاشون رو مهمون کنن! فقط کافیه عضو شی تا تو هم تو این جمع باحال باشی! {Bold('منتظرتیم!')}"""
            message.answer(welcome_message)
            # print('Profile Does Not Exist!')
            if user_info.enter_name == None:
                c = Conversation(user_id=message.chat.id)
                c.create(callback_data='enter_name')
                msg = message.text.split()
                if len(msg) > 1:
                    friends_id = msg[1]
                    c.create(callback_data=f'enter_name-{friends_id}')
                else:
                    c.create(callback_data='enter_name')
                text = '👤 نام و نام خانوادگی خود را به حروف فارسی وارد کنید, توجه داشته باشید که این نام باید مطابق با نام و نام خانوادگی درج شده روی کارت بانکی شما باشد:'
                message.answer(text)
            if user_info.enter_name != None and user_info.enter_id == None:
                c = Conversation(user_id=message.chat.id)
                msg = message.text.split()
                if len(msg) > 1:
                    friends_id = msg[1]
                    c.create(callback_data=f'enter_id-{friends_id}')
                else:
                    c.create(callback_data='enter_id')
                text = '🔹 لطفا یک نام کاربری به حروف انگلیسی برای خودتان انتخاب و ارسال کنید:'
                message.answer(text)

        except IntegrityError as e:
            # Handle the integrity error, such as unique constraint violation
            print(f"An integrity error occurred: {e}")
        except Exception as e:
            # Handle any other exceptions
            print(f"An error occurred while creating the profile: {e}")


@bot.newMessage(pattern='📢 مشاهده کانال')
def visit_channel(message):
    # impelement is joined
    setting = Setting.objects.get(id=1)
    channel = setting.channel.replace('@', '')
    url = 'https://t.me/' + channel
    keyboard = [[InlineKeyboardButton("🔗 کانال", url)]]
    keyboard = InlineKeyboardMarkup(keyboard)
    message.answer("🔹 برای دیدن کانال ما از دکمه زیر استفاده کن.", keyboard=keyboard)

@bot.newMessage(pattern='📤 ارسال لینک دعوت')
def share_invite_link(message):
    try:
        profile = Profile.objects.get(user_id=message.chat.id)
        full_name = profile.enter_name
        # referral_code = profile.referral_code
        # print(referral_code)
        me = getMe()
        u = User(**me['result'])
        # bot_id = u.id
        bot_username = u.username
        url = "http://t.me/share/url?url="
        text = f"سلام رفیق! من {full_name} هستم.\nدوست دارم باهات تو ربات مهمون شو بازی کنم!\nاگه موافق هستی که از این هفته بازی کنیم، روی لینک زیر بزن و با لینک دعوت من عضو لیست دوستان من شو.\nhttp://t.me/{bot_username}?start={profile.id}"
        encoded_url = quote(text)
        url = url + encoded_url
        keyboard = [[InlineKeyboardButton("⤴ اشتراک گذاری", url)]]
        keyboard = InlineKeyboardMarkup(keyboard)
        message.answer(text, keyboard=keyboard)
    except Profile.DoesNotExist:
        message.answer("متاسفانه، کاربری با مشخصاتی که شما وارد کرده اید در سیستم ما یافت نشد.")

def friends_management_home():
    text = """🔹 میتونی با ارسال لینک دعوت به دوستات اونا رو عضو ربات کنی تا بعد بتونی به لیست دوستات اضافه‌شون کنی.
    🔸 برای اضافه کردن دوستات میتونی از دکمه <b>افزودن دوست</b> استفاده کنی.
    🔺 برای دیدن دوستات و حذف از لیست میتونی از دکمه <b>مشاهده لیست</b> استفاده کنی."""
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن دوست", callback_data="addfriend"),
            InlineKeyboardButton("👥 مشاهده لیست", callback_data="listfriend"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(keyboard)
    return text, keyboard

@bot.newMessage(pattern='👤 ویرایش اطلاعات')
def edit_profile(message):
    try:
        profile = Profile.objects.get(user_id=message.chat.id)
        fullname = profile.enter_name
        username = profile.enter_id
        callback_data_fullname = 'editProfileFullname'
        callback_data_username = 'editProfileUsername'


        keyboard = [
            [
                InlineKeyboardButton(fullname, callback_data='null'),
                InlineKeyboardButton("نام و نام خانوادگی:", callback_data=callback_data_fullname),
            ],
            [
                InlineKeyboardButton(username, callback_data='null'),
                InlineKeyboardButton("نام کاربری:", callback_data=callback_data_username),
            ],
        ]
        keyboard = InlineKeyboardMarkup(keyboard)
        text = "در اینجا می توانید به راحتی اطلاعات پروفایل خود را ویرایش و به روز رسانی کنید. برای ویرایش هر بخش، کافی است بر روی دکمه مربوط به آن کلیک کنید."
        message.answer(text,keyboard=keyboard)
    except Profile.DoesNotExist:
        print('user not found')

@bot.newMessage(pattern='👥 لیست دوستان')
def friends_management(message):
    text, keyboard = friends_management_home()
    message.answer(text,keyboard=keyboard)

@bot.newMessage(pattern='🤖 آموزش ربات')
def bot_tutorial(message):
    try:
        setting = Setting.objects.get(id=1)
        video_link = setting.link
        sendVideo(chat_id=message.chat.id, video=video_link)
    except Setting.DoesNotExist:
        message.answer("آموزش بزودی قرار میگیرد.")

@bot.newMessage(pattern='☎ پشتیبانی')
def bot_support(message):
    try:
        profile = Profile.objects.get(user_id=message.chat.id)
        msg = Messages.objects.filter(sender=profile).last()
        # if msg and msg.status == 'OPEN':
        #     text = 'پیام قبلی شما هنوز توسط ادمین برسی نشده است. پس از برسی پیام قبلی دسترسی این بخش برای شما فعال میشود.'
        #     message.answer(text)
        # else:
        #     text = 'پیام خود را بنویس تا برای ادمین ارسال کنم:'
        #     message.answer(text)
        #     conv = Conversation(message.chat.id)
        #     conv.create('support')
        text = 'پیام خود را بنویس تا برای ادمین ارسال کنم:'
        message.answer(text)
        conv = Conversation(message.chat.id)
        conv.create('support')
    except Messages.DoesNotExist:
        text = 'پیام خود را بنویس تا برای ادمین ارسال کنم:'
        message.answer(text)
        conv = Conversation(message.chat.id)
        conv.create('support')

@bot.newMessage(pattern='🎟 قرعه‌کشی')
def lottery(message):
    setting = Setting.objects.get(id=1)
    start_time = setting.start_time
    end_time = setting.end_time
    lottery_time = setting.lottery_time

    status, msg = Check_time_validation(start_time, end_time, setting)
    if status:
        try:
            # Get the profile by ID
            profile = Profile.objects.get(user_id=message.chat.id)

            lottery, created = Lottery.objects.get_or_create(
                profile=profile,
                defaults={
                    'register_date': timezone.now(),
                    'status': 'Registering'
                }
            )
            if not created:
                if lottery.status == "Unregistered":
                    lottery = Lottery(profile=profile, register_date=timezone.now(), status='Registering')
                    lottery.save()
                    keyboard = []
                    friends = lottery.friends.all()
                    try:
                        friendList = INIsection(Bold('دوستان انتخاب شده'), [])
                        game_name = INIsection(Bold('فعالیت انتخاب شده'), ' ')
                        msg = 'لطفا یکی از بازیهای زیر رو انتخاب کنید تا در صورت برنده شدن با دوستانتون انجام بدید:'
                        text = friendList + '\n' + game_name + '\n' + msg
                        games = Games.objects.all()
                        keyboard = []
                        for game in games:
                            inline_keyboard = InlineKeyboardButton(game.name,
                                                                   callback_data=f'selectedGame-{lottery.id}-{game.id}-{game.name}')
                            keyboard.append(inline_keyboard)
                        keyboard = keyboard_generator(keyboard)
                        keyboard = InlineKeyboardMarkup(keyboard)
                        # query.message.answer(text, keyboard=keyboard)
                        # editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
                        message.answer(text, keyboard=keyboard)
                    except Games.DoesNotExist:
                        text = 'هیچ فعالیت یافت نشد!احتمالا ادمین هیچ فعالیت اضافه نکرده برای اطلاعات بیشتر با پشتیبانی تماس بگیرین.'
                        message.answer(text)
                elif lottery.status == "Registered" and lottery.payment_status == 'PENDING':
                    text = 'شما قبلا ثبت نام کرده اید, منتظر تایید ادمین باشید.'
                    message.answer(text)
                elif lottery.status == "Registered" and lottery.payment_status == 'PAID':
                    path_file = lottery.ticket_picture.url[1:]
                    # lottery_time = convert_date(lottery_time)
                    # lottery_datetime = get_date_in_current_week(lottery_time)
                    # shamsi_date = jdatetime.datetime.fromgregorian(date=lottery_datetime)
                    # lottery_time = shamsi_date.strftime('%Y/%m/%d %H:%M')
                    lottery_time = get_date_in_current_week(lottery_time)
                    msg = 'بلیط شما صادر شده.'
                    friends_name = []
                    for friend in lottery.friends.all():
                        name = friend.enter_name
                        friends_name.append(name)
                    friendList = INIsection('دوستان انتخاب شده:', friends_name)
                    game_name = INIsection('فعالیت انتخاب شده:', lottery.game.name)
                    lottery_time = f'زمان قرعه کشی:{lottery_time}'
                    text = msg + '\n' + friendList + '\n' + game_name + '\n' + lottery_time
                    sendPhoto(chat_id=message.chat.id, photo=InputFile(path_file), caption=text)
            if created or lottery.status == "Registering":
                try:
                    friendList = INIsection(Bold('دوستان انتخاب شده'), [])
                    game_name = INIsection(Bold('فعالیت انتخاب شده'), ' ')
                    msg = 'برای شرکت در قرعه کشی ابتدا از لیست فعالیت های موجود یک فعالیت را انتخاب کنید:'
                    text = friendList + '\n' + game_name + '\n' + msg
                    games = Games.objects.all()
                    keyboard = []
                    for game in games:
                        inline_keyboard = InlineKeyboardButton(game.name,
                                                               callback_data=f'selectedGame-{lottery.id}-{game.id}-{game.name}')
                        keyboard.append(inline_keyboard)
                    keyboard = keyboard_generator(keyboard)
                    keyboard = InlineKeyboardMarkup(keyboard)
                    # query.message.answer(text, keyboard=keyboard)
                    # editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
                    message.answer(text, keyboard=keyboard)
                except Games.DoesNotExist:
                    text = 'هیچ فعالیت یافت نشد!احتمالا ادمین هیچ فعالیت اضافه نکرده برای اطلاعات بیشتر با پشتیبانی تماس بگیرین.'
                    message.answer(text)
        except Profile.DoesNotExist:
            pass
    else:
        message.answer(msg)

@bot.newMessage(pattern='📚 اطلاعات قرعه کشی')
def lottery_info(message):
    setting = Setting.objects.get(id=1)
    days_of_week = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
    def conver_to_shamsi(date):
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=date)
        time_zone = jdatetime.timedelta(hours=3, minutes=30)
        # shamsi_date = shamsi_date + time_zone
        return shamsi_date
    shamsi_start_time = conver_to_shamsi(setting.start_time)
    start_time = {
        'day': days_of_week[shamsi_start_time.weekday()],
        'time': shamsi_start_time.strftime('%H:%M')
    }
    shamsi_end_time = conver_to_shamsi(setting.end_time)
    end_time = {
        'day': days_of_week[shamsi_end_time.weekday()],
        'time': shamsi_end_time.strftime('%H:%M')
    }
    shamsi_lottery_time = conver_to_shamsi(setting.lottery_time)
    lottery_time = {
        'day': days_of_week[shamsi_lottery_time.weekday()],
        'time': shamsi_lottery_time.strftime('%H:%M')
    }
    text = f"ثبت نام در قرعه کشی هر هفته از روز {Bold(start_time['day'])} ساعت {Bold(start_time['time'])} شروع میشه و روز {Bold(end_time['day'])} ساعت {Bold(end_time['time'])} تمام میشه و زمان قرعه کشیو اعلام برنده ها روز {Bold(lottery_time['day'])} ساعت {Bold(lottery_time['time'])} می باشد"
    message.answer(text)

@bot.newMessage(pattern='📊 آمار و ارقام')
def info(message):
    text = ''
    for action in ['profile', 'friends']:
        try:
            winning_lotteries = Lottery.objects.filter(winning=True)
            medals = "🥇🥈🥉🎖🎖"
            profiles = winning_lotteries.values(action).annotate(count=Count(action)).order_by('-count')
            lottery_data = []
            for index, profile in enumerate(profiles):
                # print(index, profile)
                profile_id = profile['profile'] if action == 'profile' else profile['friends']
                count = profile['count']
                # Get lottery entries for the current profile
                if profile_id:
                    profile = Profile.objects.get(id=profile_id)
                    lottery_data.append(f"{medals[index] if index <= 4 else ''} {profile.enter_name}")
            if action == 'profile':
                winners_text = INIsection(Bold('🏆 نفراتی که بیشترین بار برنده شدند'), lottery_data)
                text += '\n'+winners_text
            elif action == 'friends':
                friends_text = INIsection(Bold('👥 نفراتی که بیشترین بار به عنوان دوست برنده شدند'), lottery_data)
                text += '\n'+friends_text
        except Lottery.DoesNotExist:
            text += '\n'+ '🎖 فعلا برنده ای نداشتیم!'

    total_profiles = Profile.objects.count()
    text += '\n' + Bold('🤖 تعداد اعضای ربات') +': '+ str(total_profiles)
    message.answer(text)

def callback_query(query):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    if query.data == 'listfriend':
        try:
            # Get the profile by ID
            profile = Profile.objects.get(user_id=chat_id)
            # friends = profile.friends.all()
            friends = profileFriend.objects.filter(from_user=profile, status='Accepted')
            keyboard = []
            for friend in friends:
                profile = friend.to_user
                friend_username = profile.enter_id
                friend_id = profile.id
                keyboard.append([
                    InlineKeyboardButton(f"{friend_username}", callback_data="bck-friend"),
                    InlineKeyboardButton("❌ حذف", callback_data=f"rmfriend-{friend_id}-{chat_id}"),
                ])

            # if len(friends) > 20:
            #     keyboard.append([InlineKeyboardButton(">>", callback_data="page-1-20")])
            if friends:
                text = f"{Bold('لیست دوستات اینجاست!')}\nمیتونی توی این صفحه دوستات رو ببینی و اگه دیگه نمیخوای باهاشون دوست باشی، میتونی راحت اونا رو حذف کنی."
            else:
                text = "فقط کافیه لینک دعوت رو براشون بفرستی! بعدش میتونی لیست دوستات رو توی ربات ببینی و باهاشون بازی کنی."

            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")])
            keyboard = InlineKeyboardMarkup(keyboard)

            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        except Profile.DoesNotExist:
            # Handle case where profile with ID is not found
            pass

    if query.data == 'bck-friend':
        text, keyboard = friends_management_home()
        editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        conv = Conversation(chat_id)
        conv.cancel()

    if 'rmfriend' in query.data:
        data = query.data.split('-')
        friend_id = data[1]
        user_id = data[2]
        try:
            profile = Profile.objects.get(user_id=user_id)
            friend = profile.friends.get(id=friend_id)
            profile.friends.remove(friend)
            keyboard=[[InlineKeyboardButton("🔙 بازگشت", callback_data="listfriend")]]
            keyboard = InlineKeyboardMarkup(keyboard)
            text = 'یوزر مورد نظر با موفقیت از لیست دوستات حذف شد.'
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        except Profile.DoesNotExist:
            pass

    if query.data == 'addfriend':
        text = "فقط کافیه نام کاربری دوستت رو ازش بگیری و برام بفرستی تا به لیست دوستات اضافش کنم."
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
        keyboard = InlineKeyboardMarkup(keyboard)
        editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        conv = Conversation(chat_id)
        conv.create(callback_data='addfriend')

    if 'acceptFriend' in query.data:
        data = query.data.split('-')
        friend_id = data[1]
        # username = data[2]
        # print(f"acceptFriend: friend_id:{friend_id}, profile: {chat_id}")
        try:
            profile = Profile.objects.get(user_id=friend_id)
            friend_profile = Profile.objects.get(user_id=chat_id)

            # Update all pending friendship requests between the two users
            friendships = profileFriend.objects.filter(
                Q(from_user=profile, to_user=friend_profile) | Q(from_user=friend_profile, to_user=profile),
                status='Pending'
            )
            for friendship in friendships:
                friendship.status = 'Accepted'
                friendship.save()

            # Add friends to each other's lists (if not already added)
            if friend_profile not in profile.friends.all():
                # profile.friends.add(friend_profile)
                friendship = profileFriend(from_user=profile, to_user=friend_profile, status='Accepted')
                friendship.save()
            if profile not in friend_profile.friends.all():
                # friend_profile.friends.add(profile)
                friendship = profileFriend(from_user=friend_profile, to_user=profile, status='Accepted')
                friendship.save()

            text = 'درخواست کاربر موردنظر باموفقیت تایید شد.'
            editMessageText(text=text, message_id=query.message.message_id, chat_id=chat_id)
            text = f'کاربری با نام {Bold(friend_profile.enter_name)} نام کاربری {Bold(friend_profile.enter_id)} درخواست دوستی شمارا قبول کرد'
            sendMessage(chat_id=friend_id, text=text)
            conv = Conversation(friend_id)
            conv.cancel()
        except Profile.DoesNotExist:
            pass
    if 'cancelFriend' in query.data:
        data = query.data.split('-')
        friend_id = data[1]
        # username = data[2]
        try:
            profile = Profile.objects.get(user_id=friend_id)
            friend_profile = Profile.objects.get(user_id=chat_id)

            # Update all pending friendship requests between the two users
            friendships = profileFriend.objects.filter(
                Q(from_user=profile, to_user=friend_profile) | Q(from_user=friend_profile, to_user=profile),
                status='Pending'
            )
            for friendship in friendships:
                friendship.delete()

            text = 'درخواست کاربر موردنظر باموفقیت رد شد.'
            editMessageText(text=text, message_id=query.message.message_id, chat_id=chat_id)
            text = f'کاربری با نام {Bold(friend_profile.enter_name)} نام کاربری {Bold(friend_profile.enter_id)} درخواست دوستی شمارا رد کرد'
            sendMessage(chat_id=friend_id, text=text)
            conv = Conversation(friend_id)
            conv.cancel()
        except Profile.DoesNotExist:
            pass

    if 'editProfileFullname' in query.data:
        conv = Conversation(chat_id)
        conv.create('editProfileFullname')
        text = '👤 نام و نام خانوادگی خود را به حروف فارسی وارد کنید:'
        sendMessage(chat_id=chat_id, text=text)

    if 'editProfileUsername' in query.data:
        conv = Conversation(chat_id)
        conv.create('editProfileUsername')
        text = '🔹 لطفا یک نام کاربری به حروف انگلیسی برای خودتان انتخاب و ارسال کنید:'
        sendMessage(chat_id=chat_id, text=text)

    if 'selectFriend' in query.data:
        data = query.data.split('-')
        lottery_id = data[1]
        lottery = Lottery.objects.get(id=lottery_id)
        friends = lottery.profile.friends.all()
        keyboard = []
        if len(friends) != 0:
            for friend in friends:
                friend_name = friend.enter_name
                friend_id = friend.id
                keyboard.append([
                    InlineKeyboardButton(f"❌ {friend_name}",
                                         callback_data=f"selectedFriend-{friend_id}-{lottery.id}-{friend_name}"),
                ])

            keyboard.append([
                InlineKeyboardButton("بازگشت",
                                     callback_data=f"selectedGame-{lottery.id}-{lottery.game.id}-{lottery.game.name}"),
            ])
            game_name = lottery.game.name
            friendList = INIsection(Bold('دوستان انتخاب شده'), [])
            game_name = INIsection(Bold('فعالیت انتخاب شده'), game_name)
            msg = 'برای شرکت در قرعه کشی ابتدا باید از لیست زیر دوستان خودرا انتخاب کنید:'
            text = friendList + '\n' + game_name + '\n' + msg
            keyboard = InlineKeyboardMarkup(keyboard)
            # query.message.answer(text, keyboard=keyboard)
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        else:
            text = 'شماه هیچ دوستی ندارید.\nلطفا از قسمت "➕ افزودن دوست" اقدام به اضافه کردن دوستان خود کنید.'
            keyboard = [
                [
                    InlineKeyboardButton("➕ افزودن دوست", callback_data="addfriend"),
                ],
            ]
            keyboard = InlineKeyboardMarkup(keyboard)
            # query.message.answer(text, keyboard=keyboard)
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)

    if 'selectedFriend' in query.data:
        data = query.data.split('-')
        friend_id = data[1]
        lottery_id = data[2]
        friend_name = data[3]
        print(query.data)
        try:
            lottery = Lottery.objects.get(id=lottery_id)
            profile = Profile.objects.get(id=friend_id)

            keyboard = query.message.reply_markup['inline_keyboard']
            for k in keyboard:
                print(k)
            for inner_list in keyboard:
                for item in inner_list:
                    if item['text'] == 'بازگشت':
                        print('bck removed')
                        keyboard.remove(inner_list)
                    elif item['text'] == '💳 رفتن به مرحله پرداخت':
                        keyboard.remove(inner_list)
                    elif item['text'] == '📑 ارسال فیش پرداخت':
                        keyboard.remove(inner_list)
                    elif item["callback_data"] == query.data:
                        if "✅" not in item["text"]:
                            # text = f"✅ {item['text']}"
                            text = item["text"].replace("❌ ", "✅ ")
                            lottery.friends.add(profile)
                        else:
                            text = item["text"].replace("✅ ", "❌ ")
                            lottery.friends.remove(profile)
                        item.update({"text": text})
            friendList = []
            for friend in lottery.friends.all():
                name = friend.enter_name
                friendList.append(name)
            if len(friendList):
                payment = InlineKeyboardButton('💳 رفتن به مرحله پرداخت', callback_data=f"payment-{friend_id}-{lottery_id}-{friend_name}")
                if [payment] not in keyboard:
                    keyboard.append([payment])
                    bck = [
                        InlineKeyboardButton("بازگشت",
                                             callback_data=f"selectedGame-{lottery.id}-{lottery.game.id}-{lottery.game.name}"),
                    ]
                    if bck in keyboard:
                        keyboard.remove(bck)
                    keyboard.append(bck)

            keyboard = InlineKeyboardMarkup(keyboard)
            friendList = INIsection(Bold('دوستان انتخاب شده'), friendList)
            game_name = lottery.game.name
            game_name = INIsection(Bold('فعالیت انتخاب شده'), game_name)
            msg = 'برای شرکت در قرعه کشی ابتدا باید از لیست زیر دوستان خودرا انتخاب کنید:'
            text = friendList + '\n' + game_name + '\n' + msg
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)

        except Lottery.DoesNotExist:
            # print('lottery does not exist.')
            pass

    if 'selectedGame' in query.data:
        data = query.data.split('-')
        lottery_id = data[1]
        game_id = data[2]
        game_name = data[3]
        try:
            games = Games.objects.all()
            keyboard = []
            for game in games:
                gameName = "✅ "+game.name if game.name == game_name else game.name
                # print(game_name, gameName, game.name)
                inline_keyboard = InlineKeyboardButton(gameName, callback_data=f'selectedGame-{lottery_id}-{game.id}-{gameName}')
                keyboard.append(inline_keyboard)

            keyboard = keyboard_generator(keyboard)
            if '✅' not in game_name:
                keyboard.append([
                        InlineKeyboardButton('رفتن به انتخاب دوستان', callback_data=f"selectFriend-{lottery_id}")
                ])
            keyboard = InlineKeyboardMarkup(keyboard)
            lottery = Lottery.objects.get(id=lottery_id)
            lottery.game = Games.objects.get(id=game_id)
            lottery.save()
            friendList = INIsection(Bold('دوستان انتخاب شده'), [])
            game_name = '' if '✅' in game_name else game_name
            game_name = INIsection(Bold('فعالیت انتخاب شده'), game_name)
            msg = 'برای شرکت در قرعه کشی ابتدا باید از لیست زیر دوستان خودرا انتخاب کنید:'
            text = friendList + '\n' + game_name + '\n' + msg
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)

        except Games.DoesNotExist:
            text = 'هیچ فعالیت یافت نشد!احتمالا ادمین هیچ فعالیت اضافه نکرده برای اطلاعات بیشتر با پشتیبانی تماس بگیرین.'
            query.message.answer(text)

    if 'payment' in query.data:
        data = query.data.split('-')
        friend_id = data[1]
        lottery_id = data[2]
        friend_name = data[3]

        setting = Setting.objects.get(id=1)
        card_number = Bold(setting.card_number)
        card_name = Bold(setting.card_name)
        payment_price = Bold(setting.price)
        payment_method = setting.payment_method
        # merchant_id = setting.merchant_id
        merchant_id = djagno_settings.MERCHANT
        if payment_method == 'card-to-card':
            # text = "برای واریز مبلغ مورد نظر، لطفا به شماره کارت {card_number} به نام {card_name} وجه {payment_price} تومان را انتقال دهید.\nسپس با فشردن دکمه زیر عکس فیش واریزی خود را ارسال کنید."
            text = f"لطفا مبلغ {payment_price} تومان را به شماره کارت زیر واریز نمایید و با فشردن دکمه زیر عکس فیش واریزی خود را ارسال کنید."
            text += "\n" + f"{card_number}" + "\n" + f"{card_name}"
            keyboard = [
                [
                    InlineKeyboardButton("📑 ارسال فیش پرداخت", callback_data=f"paid-{lottery_id}"),
                ],
                [
                    InlineKeyboardButton("بازگشت",
                                         callback_data=f"selectFriend-{lottery_id}"),
                ]
            ]
            keyboard = InlineKeyboardMarkup(keyboard)
            editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)
        else:
            # print('gateway')
            # create new payment
            payment = Payment.objects.create(
                amount=setting.price,
                payment_method='gateway',
                lottery_id=lottery_id
            )
            payment_id = payment.id
            description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
            PAYMENT_CALLBACK_URL = djagno_settings.PAYMENT_CALLBACK_URL

            data = {
                "merchant_id": merchant_id,
                "amount": str(setting.price),
                "currency": "IRT",
                "description": description,
                "callback_url": PAYMENT_CALLBACK_URL,
                "metadata": {
                    'order_id': str(payment.id),
                }
            }
            data = json.dumps(data)
            # ? sandbox merchant
            if djagno_settings.SANDBOX:
                sandbox = 'sandbox'
            else:
                sandbox = 'payment'

            ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
            ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

            # set content length by data
            headers = {'content-type': 'application/json', 'content-length': str(len(data))}
            try:
                # print(ZP_API_REQUEST)
                response = session.post(ZP_API_REQUEST, data=data, headers=headers, timeout=100)
                # print(response.json())
                if response.status_code == 200:
                    response = response.json()['data']
                    print(response)
                    if response['code'] == 100:
                        payment = Payment.objects.get(id=payment_id)
                        payment.authority = response['authority']
                        payment.save()
                        url = ZP_API_STARTPAY + str(response['authority'])
                        keyboard = [[InlineKeyboardButton("🔗 درگاه پرداخت", url)]]
                        keyboard = InlineKeyboardMarkup(keyboard)
                        text = f"لطفا مبلغ {payment_price} تومان را با فشردن دکمه زیر از طریق درگاه پرداخت واریز نمایید."
                        editMessageText(text=text, reply_markup=keyboard, chat_id=chat_id, message_id=message_id)

                    else:
                        text = f"خطا در ارسال درخواست. کد خطا {str(response['code'])}"
                        query.message.answer(text)
                else:
                    text = "خطا در اتصال لطفا دقایقی دیگر دوباره امتحان کنید!"
                    query.message.answer(text)
            except requests.exceptions.Timeout:
                text = f"زمان پرداخت شما به پایان رسید. کد خطا {str(response['code'])}"
                query.message.answer(text)

            except requests.exceptions.ConnectionError:
                text = "خطا در اتصال لطفا دوباره امتحان کنید!"
                query.message.answer(text)

    if 'paid' in query.data:
        data = query.data.split('-')
        lottery_id = data[1]
        conv = Conversation(chat_id)
        conv.create('paid')
        lottery = Lottery.objects.get(id=lottery_id, status='Registering')
        lottery.status = 'Registered'
        lottery.save()
        text = 'لطفا عکس فیش واریزی خود را ارسال کنید:'
        query.message.answer(text)

def filter_message(message):
  try:
      text = message.text or message.caption
      if text:
          patterns = ['^/start', '📢 مشاهده کانال', '📤 ارسال لینک دعوت', '👤 ویرایش اطلاعات', '👥 لیست دوستان', '🤖 آموزش ربات', '☎ پشتیبانی', '🎟 قرعه‌کشی', '📊 آمار و ارقام', '📚 اطلاعات قرعه کشی']
          compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
          for pattern in compiled_patterns:
              match = pattern.search(text)
              if match:
                  return True
          return False
      else:
          return False
  except AttributeError as e:
    print(f"Error accessing message attributes: {e}")
    return False

def any(message):
    # Perform conversation tasks
    conv = Conversation(message.chat.id)
    data = conv.data()
    print('conversations:', data)

    if data and (filter_message(message)==False):
        print('callback_data is: ', data['callback_data'])
        if data['callback_data'] == 'paid':
            try:
                profile = Profile.objects.get(user_id=message.chat.id)
                # if message.photo != None:
                #     lottery = Lottery.objects.filter(profile=profile).last()
                #     file_id = message.photo[-1].file_id
                #     f = getFile(file_id)
                #     file_path = f['result']['file_path']
                #     filename = get_filename_with_date(message.chat.id, '.jpg')
                #     pic = bot.download_file(filename=filename, dir_path='media/img/uploads', file_path=file_path)
                #     filename = 'img/uploads/' + filename
                #     lottery.payment_picture = filename
                #     lottery.save()
                #     text = 'فیش شما با موفقیت ارسال شد منتظر تایید ادمین باشید.'
                #     message.answer(text)
                #     conv.cancel()
                #
                #     setting = Setting.objects.get(id=1)
                #     if setting.total_payments is not None:
                #         setting.total_payments += 1
                #     else:
                #         setting.total_payments = 0
                #     # Broadcast the message to all connected clients
                #     data = {
                #         'total_unread_messages': setting.total_unread_messages,
                #         'total_new_payments': setting.total_payments,
                #     }
                #     channel_layer = get_channel_layer()
                #     async_to_sync(channel_layer.group_send)('unread', {
                #         'type': 'chat_message',
                #         'message': json.dumps({
                #             'data': data,
                #         }),
                #     })

            except Profile.DoesNotExist:
                pass
        if 'enter_name' in data['callback_data']:
            if is_persian_name(message.text):
                try:
                    profile = Profile.objects.get(user_id=message.chat.id)
                    profile.enter_name = message.text
                    profile.save()

                    callback_data = data['callback_data'].split('-')
                    if len(callback_data) > 1:
                        friends_id = callback_data[1]
                        conv.change_callback_data(callback_data=f'enter_id-{friends_id}')
                    else:
                        conv.change_callback_data(callback_data='enter_id')

                    text = '🔹 لطفا یک نام کاربری به حروف انگلیسی برای خودتان انتخاب و ارسال کنید:'
                    message.answer(text)
                except Profile.DoesNotExist:
                    pass
            else:
                message.answer(f"خطا! لطفا نام و نام خانوادگی خود را با {Bold('حروف فارسی')} وارد کنید")

        if 'enter_id' in data['callback_data']:
            text_status, msg = is_valid_username(message.text)
            if text_status:
                try:
                    profile = Profile.objects.get(user_id=message.chat.id)
                    profile.enter_id = message.text.lower()
                    profile.status = 'Registered'
                    profile.save()
                    conv.cancel()
                    text = '✅ اطلاعاتت با موفقیت تکمیل شد!'
                    keyboard = [
                        [KeyboardButton('🎟 قرعه‌کشی')],
                        [KeyboardButton('📚 اطلاعات قرعه کشی'),KeyboardButton('📤 ارسال لینک دعوت'),KeyboardButton('📢 مشاهده کانال'),],
                        [KeyboardButton('👤 ویرایش اطلاعات'),KeyboardButton('👥 لیست دوستان'),],
                        [
                            KeyboardButton('☎ پشتیبانی'),
                            KeyboardButton('📊 آمار و ارقام'),
                            KeyboardButton('🤖 آموزش ربات'),
                        ],
                    ]
                    keyboard = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
                    message.answer(text, keyboard=keyboard)

                    # invite link:
                    callback_data = data['callback_data'].split('-')
                    if len(callback_data) > 1:
                        firend_id = callback_data[1]
                        invietfrend(message=message, friends_id=firend_id)

                except IntegrityError:
                    text = 'نام کاربری وارد شده در سیستم وجود دارد. یک نام کاربری دیگر را تست کنید.'
                    message.answer(text)
            else:
                message.answer(msg)
        if data['callback_data'] == 'addfriend':
            try:
                profile = Profile.objects.get(user_id=message.chat.id)
                friend_profile = Profile.objects.get(enter_id=message.text.lower())
                # Check if a friendship already exists between these two users
                friendship, created = profileFriend.objects.get_or_create(
                    from_user=profile,
                    to_user=friend_profile,
                    defaults={"status": 'Pending'},
                )
                # if created send request to user
                if created:
                    # Check if friend is already in user's friend list
                    text = f"کاربری با نام {profile.enter_name} و نام کاربری {profile.enter_id} برای شما درخواست دوستی فرستاده.از دکمه زیر برای تایید درخواست استفاده کنید.{Bold('توجه داشته باشد بعد از تایید به لیست دوستان یکدیگر اضافه میشوید.')}"
                    keyboard = [
                        [
                            InlineKeyboardButton("✅ تایید",
                                                 callback_data=f"acceptFriend-{message.chat.id}-{message.text.lower()}"),
                            InlineKeyboardButton("❌ رد",
                                                 callback_data=f"cancelFriend-{message.chat.id}-{message.text.lower()}"),
                        ]
                    ]
                    keyboard = InlineKeyboardMarkup(keyboard)
                    sendMessage(chat_id=friend_profile.user_id, text=text, reply_markup=keyboard)
                    text = 'درخواست دوستی شما برای کاربر مورد نظر ارسال شد پس از تایید, به لیست دوستات اضافه میشه.\nبرای اضافه کردن دوستان بیشتر از دکمه بازگشت استاده کنید.'
                    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
                    keyboard = InlineKeyboardMarkup(keyboard)
                    message.reply(text=text, keyboard=keyboard)
                # If the friendship already exists, update the status
                if not created:
                    if friendship.status == 'Pending':
                        text = 'شما قبلا برای این کاربر درخواست دوستی فرستادین!\nیک نام کاربری دیگر را وارد کنید یا دکمه بازگشت را برای لفو عملیات بزنید.'
                        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
                        keyboard = InlineKeyboardMarkup(keyboard)
                        message.reply(text=text, keyboard=keyboard)
                    if friendship.status == 'Accepted':
                        text = 'در حال حاظر این کاربر در لیست دوستان شما قرار دارد\nیک نام کاربری دیگر را وارد کنید یا دکمه بازگشت را برای لفو عملیات بزنید.'
                        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
                        keyboard = InlineKeyboardMarkup(keyboard)
                        message.reply(text=text, keyboard=keyboard)

            except Profile.DoesNotExist:
                text = 'هیچ کاربری با این نام کاربری در سیستم وجود ندارد\nیک نام کاربری دیگر را وارد کنید یا دکمه بازگشت را برای لفو عملیات بزنید.'
                keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="bck-friend")]]
                keyboard = InlineKeyboardMarkup(keyboard)
                message.reply(text=text, keyboard=keyboard)

        if data['callback_data'] == 'editProfileFullname':
            try:
                if is_persian_name(message.text):
                    profile = Profile.objects.get(user_id=message.chat.id)
                    profile.enter_name = message.text
                    profile.save()
                    conv.cancel()
                    text = 'نام و نام خانوادگی شما با موفقیت ویرایش شد.'
                    message.answer(text)
                else:
                    message.answer(f"خطا! لطفا نام و نام خانوادگی خود را با {Bold('حروف فارسی')} وارد کنید")
            except Profile.DoesNotExist:
                pass
        if data['callback_data'] == 'editProfileUsername':
            text_status, msg = is_valid_username(message.text)
            if text_status:
                try:
                    profile = Profile.objects.get(user_id=message.chat.id)
                    profile.enter_id = message.text.lower()
                    profile.save()
                    conv.cancel()
                    text = 'نام کاربری شما با موفقیت ویرایش شد.'
                    message.answer(text)
                except IntegrityError:
                    text = 'نام کاربری وارد شده در سیستم وجود دارد. یک نام کاربری دیگر را تست کنید.'
                    message.answer(text)
                except Profile.DoesNotExist:
                    pass
            else:
                message.answer(msg)
        if data['callback_data'] == 'support':
            if message.photo or message.text:
                try:
                    profile = Profile.objects.get(user_id=message.chat.id)
                    if message.photo == None:
                        messageObj = Messages.objects.create(sender=profile, message=message.text)
                        message_text = message.text
                    else:
                        file_id = message.photo[-1].file_id
                        f = getFile(file_id)
                        file_path = f['result']['file_path']
                        filename = get_filename_with_date(message.chat.id, '.jpg')
                        pic = bot.download_file(filename=filename, dir_path='media/img/uploads/', file_path=file_path)
                        filename = 'img/uploads/' + filename
                        messageObj = Messages.objects.create(sender=profile, message=message.caption, sender_picture=filename)
                        message_text = message.caption
                    text = 'پیام شما با موفقیت ارسال شد.'
                    message.answer(text)
                    conv.cancel()

                    if profile.unread_message_number is not None:
                        profile.unread_message_number += 1
                        profile.save()
                    else:
                        profile.unread_message_number = 1
                        profile.save()
                    setting = Setting.objects.get(id=1)
                    if setting.total_unread_messages is not None:
                        setting.total_unread_messages += 1
                    else:
                        setting.total_unread_messages = 0
                    setting.save()

                    # Broadcast the message to all connected clients
                    data = {
                        'total_unread_messages': setting.total_unread_messages,
                        'total_new_payments': setting.total_payments,
                        'enter_id': messageObj.sender.enter_id,
                    }
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)('unread', {
                        'type': 'chat_message',
                        'message': json.dumps({
                            'data': data,
                        }),
                    })

                    shamsi_date = jdatetime.datetime.fromgregorian(datetime=messageObj.created_at)
                    sender_profile = messageObj.sender
                    message_data = {
                        'id': messageObj.id,
                        'message': messageObj.message,
                        'answer': messageObj.answer,
                        'sender_picture': messageObj.sender_picture.url if messageObj.sender_picture else None,
                        'answer_picture': messageObj.answer_picture.url if messageObj.answer_picture else None,
                        'sender_profile': {
                            'enter_name': sender_profile.enter_name,
                            'enter_id': sender_profile.enter_id,
                            'picture': sender_profile.picture.url if sender_profile.picture else None,
                        },
                        'datetime': shamsi_date.strftime('%H:%M %Y/%m/%d'),
                        'status': messageObj.status,
                    }

                    contact_data = {
                        'id': profile.id,
                        'enter_name': profile.enter_name,
                        'enter_id': profile.enter_id,
                        'user_id': profile.user_id,
                        'profile_id': profile.id,
                        'profile_picture': profile.picture.url if profile.picture else None,
                        'total_unread_messages': profile.unread_message_number,
                        'last_message': message_text,
                    }
                    # Broadcast the message to all connected clients
                    data = {
                        'total_unread_messages': setting.total_unread_messages,
                        'unread_message_number': profile.unread_message_number,
                        'profile_id': profile.id,
                        'message_data': message_data,
                        'contact_data': contact_data,
                    }
                    async_to_sync(channel_layer.group_send)('unreadmessage', {
                        'type': 'chat_message',
                        'message': json.dumps({
                            'data': data,
                        }),
                    })
                except Profile.DoesNotExist:
                    pass
            else:
                text = 'خطا! پیام ارسالی شما باید متن یا عکس کپشن دار باشد.'
                message.answer(text)


    # print(message.text, message.text == '/webapp')
    if message.text == '/webapp':
        text = 'we are testing webapp...'
        message.answer(text)
        web_app = WebAppInfo(url="https://mybotadmin.site/")
        keyboard = [
            [InlineKeyboardButton("click me!", web_app=web_app)],
        ]
        keyboard = InlineKeyboardMarkup(keyboard)
        text = 'this is web app! click to below btn to open it.'
        message.answer(text, keyboard=keyboard)

UPDATE_HANDLER = {
    'message': [start, any, visit_channel, share_invite_link, friends_management, edit_profile, bot_tutorial, bot_support, lottery, lottery_info, info],
    'callback_query': [callback_query, ]
}
@csrf_exempt
def uph(request):
    return UpdateHandler(request, UPDATE_HANDLER)