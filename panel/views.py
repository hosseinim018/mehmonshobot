from django.shortcuts import render, redirect
from panel.models import *
from django.http import JsonResponse
import json
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from monogram.methods import sendMessage, sendPhoto
from monogram.types import InputFile
from monogram.text import INIsection, Bold
import jdatetime
from panel.assist import generate_ticket, get_time
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User

def convert_date(date):
    if date:
        # Convert to Shamsi date
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=date)
        time_zone = jdatetime.timedelta(hours=3, minutes=30)
        shamsi_date = shamsi_date + time_zone
        # Update the field in the dictionary
        return shamsi_date.strftime('%H:%M %Y/%m/%d')
    else:
        current_datetime = jdatetime.datetime.now()
        return current_datetime.strftime('%H:%M %Y/%m/%d')


def generate_response(data=None, message='successful', error=None, status_code=200):
  """
  Generates a dictionary representing a response object.

  Args:
      data (dict, optional): Data to include in the response. Defaults to None.
      message (str, optional): Message to include in the response. Defaults to None.
      error (str, optional): Error message to include in the response. Defaults to None.
      status_code (int, optional): HTTP status code for the response. Defaults to 200.

  Returns:
      dict: A dictionary representing the response structure.
  """

  response = {'status_code': status_code}

  if data:
    response['data'] = data
  if message:
    response['message'] = message
  if error:
    response['error'] = error

  return response


from django.shortcuts import redirect
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('Login')
    return wrapper

# Create your views here
@login_required
def home(request):
    return render(request, 'index.html')

@login_required
def ProfileView(request):
    return render(request, 'Profile.html')

@login_required
def MessagesView(request):
    return render(request, 'Messages.html')

@login_required
def WinningView(request):
    return render(request, 'Winning.html')

@login_required
def PaymentsView(request):
    return render(request, 'Payments.html')

@login_required
def SettingsView(request):
    return render(request, 'Settings.html')

def register(request):
    username = request.GET.get('username')
    password1 = request.GET.get('password1')
    password2 = request.GET.get('password2')
    email = request.GET.get('email')
    print(username, password1, password2, email)
    if request.method == 'POST':
        # form = SignUpForm({'username': username, 'password1': password1, 'password2': password2, 'email': email})
        form = SignUpForm(request.GET)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password, email=email)
            login(request, user)
            request.session['user_id'] = user.id
            return JsonResponse(generate_response(message='register_successful'))
        else:
            return JsonResponse(generate_response(message='register_errors', data=form.errors.as_json()))

    return JsonResponse(generate_response(message='register_errors'))


@csrf_exempt
def LoginView(request):
    if request.method == 'POST':
        username = request.GET.get('username')
        password = request.GET.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Login successful
            request.session['user_id'] = user.id
            return JsonResponse(generate_response(message='successful'))
        else:
            # Login failed
            return JsonResponse(generate_response(message='حطا در ورود: نام کاربری یا یوزرنیم بافت نشد!', error='Login failed', status_code=404), status=401)
    else:
        return render(request, 'Login.html')

@csrf_exempt
def LogoutView(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse(generate_response(message='successful'))
    else:
        # Login failed
        return JsonResponse(generate_response(error='Logout failed'))

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

def serialize_form(form):
    return {
        'data': form.data,
        'errors': form.errors.as_json(),
        'fields': {name: str(field) for name, field in form.fields.items()}
    }

@csrf_exempt
def password_reset_view(request):
    username = request.GET.get('username')
    if username:
        try:
            user = User.objects.filter(username=username).first()

            token = default_token_generator.make_token(user)
            if default_token_generator.check_token(user, token):
                if request.method == 'POST':
                    password1 = request.GET.get('new_password1')
                    password2 = request.GET.get('new_password2')
                    print(password1, password2)
                    # form = SetPasswordForm(user, request.POST)
                    # form = SetPasswordForm(user, data={'new_password1': password1, 'new_password2': password2})
                    form = SetPasswordForm(user, {
                        'new_password1': password1,
                        'new_password2': password2
                    })
                    if form.is_valid():
                        form.save()
                        print('valid')
                        return JsonResponse(generate_response(message='password_reset_successful'))
                    else:
                        print(form.errors)
                        return JsonResponse(generate_response(message='password_reset_errors', data=form.errors.as_json()))

                if request.method == 'GET':
                    return JsonResponse(generate_response(message='password_reset_confirm'))
            else:
                return JsonResponse(generate_response(message='The password reset link is invalid.', status_code=404))
        except User.DoesNotExist:
            # Handle case where profile with ID is not found
            return JsonResponse(generate_response(error='User not found', status_code=404))
    return JsonResponse(generate_response(message='Username not found', status_code=404))


def password_reset_confirm_view(request):
    user = User.objects.get(id=1)
    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})



def LotteryView(request):
    return render(request, 'Lottery.html')

def InfoView(request):
    return render(request, 'Info.html')


def get_users(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()  # Get all Profile objects
        profile_list = []
        for profile in profiles:
            # Create a dictionary for each profile
            profile_dict = {
                'id': profile.id,
                'profile': {'name': profile.full_name, 'username': profile.username},
                'fullName': profile.enter_name,
                'userId': profile.enter_id,
                'picture': profile.picture.url if profile.picture else None,  # Handle potential missing picture
            }
            profile_list.append(profile_dict)

        return JsonResponse(generate_response(data=profile_list))

@csrf_exempt
def load_profile_based_on_id(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    if profile_id:
      try:
        # Get the profile by ID
        profile = Profile.objects.filter(id=profile_id)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(profile.values())))
      except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))


def recordChangesOfProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    enter_id = request.GET.get('enter_id')
    enter_name = request.GET.get('enter_name')
    # referral_code = request.GET.get('referral_code')

    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        # Update the profile object with new values
        # profile.referral_code = referral_code
        profile.enter_name = enter_name
        profile.enter_id = enter_id

        # Save the updated profile
        profile.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def loadProfileFriends(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        friends = profile.friends.all()
        profile_list = []
        for profile in friends:
            # Create a dictionary for each profile
            profile_dict = {
                "enter_id": profile.enter_id,
                "enter_name": profile.enter_name,
                "full_name": profile.full_name,
                "id": profile.id,
                # "login_code": profile.login_code,
                "picture": profile.picture.url if profile.picture else None,
                # "referral_code": profile.referral_code,
                "user_id": profile.user_id,
                "username": profile.username,
            }
            profile_list.append(profile_dict)

        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=profile_list))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def loadMessagesyHistoryOfProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        messages = Messages.objects.filter(sender=profile_id)
        message_data = []
        for message in messages:
            shamsi_date = jdatetime.datetime.fromgregorian(datetime=message.created_at)
            sender_profile = message.sender
            message_data.append({
                'id': message.id,
                'message': message.message,
                'answer': message.answer,
                'sender_picture': message.sender_picture.url if message.sender_picture else None,
                'answer_picture': message.answer_picture.url if message.answer_picture else None,
                'sender_profile': {
                    'enter_name': sender_profile.enter_name,
                    'enter_id': sender_profile.enter_id,
                    'picture': sender_profile.picture.url if sender_profile.picture else None,
                },
                'datetime': shamsi_date.strftime('%H:%M %Y/%m/%d'),
                'status': message.status
            })
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=message_data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def loadMessagesyHistory(request):
    # Get the profile by ID
    messages = Messages.objects.prefetch_related('sender').all()
    message_data = []
    for message in messages:
        # print(message.answer_picture)
        sender_profile = message.sender
        print(sender_profile.picture)
        message_data.append({
            'id': message.id,
            'message': message.message,
            'answer': message.answer,
            'sender_picture': message.sender_picture.url if message.sender_picture else None,
            'answer_picture': message.answer_picture.url if message.answer_picture else None,
            'sender_profile': {
                'enter_name': sender_profile.enter_name,
                'enter_id': sender_profile.enter_id,
                'picture': sender_profile.picture.url if sender_profile.picture else None,  # Handle potential missing picture
            }
        })
    # Return profile data as a dictionary
    return JsonResponse(generate_response(message='successful', data=message_data))

def loadMessagesContents(request):
    senders = Messages.objects.values_list('sender__pk', flat=True).distinct()
    sender_data = []
    for id in senders:
        profile = Profile.objects.get(id=id)
        msg = Messages.objects.filter(sender=profile, status='OPEN')
        last_message = msg.order_by('-created_at').first()
        total_unread_messages = msg.count()
        sender_info = {
            'id': id,
            'enter_name': profile.enter_name,
            'enter_id': profile.enter_id,
            'user_id': profile.user_id,
            'profile_picture': profile.picture.url if profile.picture else None,
            'total_unread_messages': total_unread_messages,
            'last_message': last_message.message if last_message else None,
        }
        sender_data.append(sender_info)
    return JsonResponse(generate_response(message='successful', data=sender_data))

def deleteMessage(request):
    # Access ID from POST data
    message_id = request.GET.get('id')
    try:
        # Get the profile by ID
        message = Messages.objects.get(id=message_id)
        message.delete() # Delete the retrieved profile

        setting = Setting.objects.get(id=1)
        if setting.total_unread_messages is not None:
            setting.total_unread_messages -= 1
        else:
            setting.total_unread_messages = 0
        setting.save()
        # Broadcast the message to all connected clients
        data = {
            'total_unread_messages': setting.total_unread_messages,
            'total_new_payments': setting.total_payments,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('unread', {
            'type': 'chat_message',
            'message': json.dumps({
                'data': data,
            }),
        })

        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='message deleted successfully'))
    except Messages.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='message not found', status_code=404))

def closeMessage(request):
    # Access ID from POST data
    message_id = request.GET.get('id')
    try:
        # Get the profile by ID
        message = Messages.objects.get(id=message_id)
        message.status = 'CLOSED'
        message.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='message closed successfully'))
    except Messages.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='message not found', status_code=404))

def deleteProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)
        profile.delete() # Delete the retrieved profile
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='Profile deleted successfully'))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)

        lotteries = profile.lottery_entries.all()
        data = []
        for lottery in list(lotteries.values()):
            l = Lottery.objects.get(pk=lottery['id'])
            lottery['game'] = l.game.name if l.game else ''
            friends = l.friends.all()
            lottery['friends'] = [{'id': f['id'], 'enter_name': f['enter_name']} for f in friends.values()]
            lottery['register_date'] = convert_date(lottery['register_date'])
            lottery['payment_picture'] = l.payment_picture.url if l.payment_picture else None,
            # print(lottery['register_date'])
            data.append(lottery)
        # print(data)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryWinningProfile(request):
    # Access ID from POST data
    profile_id = request.GET.get('id')
    try:
        # Get the profile by ID
        profile = Profile.objects.get(id=profile_id)

        lotteries = profile.lottery_entries.all()
        lotteries = lotteries.filter(winning=True)

        data = []
        for lottery in list(lotteries.values()):
            l = Lottery.objects.get(pk=lottery['id'])
            friends = l.friends.all()
            lottery['friends'] = [{'id': f['id'], 'enter_name': f['enter_name']} for f in friends.values()]
            lottery['game'] = l.game.name if l.game else ''
            lottery['payment_picture'] = l.payment_picture.url if l.payment_picture else None,
            lottery['register_date'] = convert_date(lottery['register_date'])
            data.append(lottery)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=data))
    except Profile.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))

def modalHandlerLotteryWinning(request):
    winning_lotteries = Lottery.objects.select_related('profile').filter(winning=True)  # Adjust filter criteria as needed

    # Prepare data for rendering (optional)
    lottery_data = []
    for lottery in winning_lotteries:
        lottery_data.append({
            'id': lottery.id,
            'profile_id': lottery.profile.id,
            'register_date': convert_date(lottery.register_date),
            'game': lottery.game.name if lottery.game else '',
            'ticket': lottery.ticket,
            'payment_status': lottery.payment_status,
            'friends': [{'id': f['id'], 'enter_name': f['enter_name']} for f in lottery.friends.values()],
            'enter_name': lottery.profile.enter_name,
            'enter_id': lottery.profile.enter_id,
        })
    # Return profile data as a dictionary
    return JsonResponse(generate_response(message='successful', data=lottery_data))


def sortLotteryBasedOnHighest(request):
    action = request.GET.get('action')
    # Filter for winning records (winning=True)
    winning_lotteries = Lottery.objects.filter(winning=True)

    # Count the number of wins for each profile
    profile_counts = winning_lotteries.values('profile', action).annotate(count=Count(action)).order_by('-count')
    lottery_data = []
    for profile_count in profile_counts:
        profile_id = profile_count['profile']
        count = profile_count['count']

        # Get lottery entries for the current profile
        lottery_entries = Lottery.objects.filter(profile_id=profile_id, winning=True)

        # Loop through lottery entries and build the data dictionary
        for lottery in lottery_entries:

            lottery_data.append({
                'id': lottery.id,
                'register_date': convert_date(lottery.register_date),
                'game': lottery.game.name,  # Assuming 'game' has a related field with 'name'
                'ticket': lottery.ticket,
                'payment_status': lottery.payment_status,
                'price': lottery.price,
                'number_in_cart': lottery.number_in_cart,
                'friends': [{'id': f.id, 'enter_name': f.enter_name} for f in lottery.friends.all()],
                # Access all friends
                'enter_name': lottery.profile.enter_name,
                'enter_id': lottery.profile.enter_id,
            })

    # print(winning_lotteries.values('profile'))
    return JsonResponse(generate_response(message='successful', data=lottery_data))



def addAdmin(request):
    # Access ID from POST data
    name = request.GET.get('name')
    id = request.GET.get('id')
    try:
        # Get the profile by ID
        admin = Admins()
        admin.name = name
        admin.user_id = id
        admin.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getAdmins(request):
    try:
        # Get the profile by ID
        admin = Admins.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(admin.values())))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def removeAdmin(request):
    id = request.GET.get('id')
    try:
        admin = Admins.objects.get(id=id)
        admin.delete()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def addGame(request):
    # Access ID from POST data
    name = request.GET.get('name')
    try:
        # Get the profile by ID
        game = Games()
        game.name = name
        game.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getGames(request):
    try:
        # Get the profile by ID
        game = Games.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(game.values())))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def removeGame(request):
    id = request.GET.get('id')
    try:
        game = Games.objects.get(id=id)
        game.delete()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Games.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))



def setCard(request):
    # Access ID from POST data
    card_name = request.GET.get('card_name')
    card_number = request.GET.get('card_number')
    price = request.GET.get('price')
    payment_method = request.GET.get('payment_method')
    try:
        # Get the profile by ID
        setting = Setting()
        setting.card_name = card_name
        setting.card_number = card_number
        setting.price = price
        setting.payment_method = payment_method
        setting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def updateCard(request):
    # Access ID from POST data
    card_name = request.GET.get('card_name')
    card_number = request.GET.get('card_number')
    price = request.GET.get('price')
    payment_method = request.GET.get('payment_method')
    try:
        # Get the profile by ID
        setting = Setting.objects.get(id=1)
        setting.card_name = card_name
        setting.card_number = card_number
        setting.price = price
        setting.payment_method = payment_method
        setting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Admins.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))

def getSettings(request):
    try:
        # Get the profile by ID
        setting = Setting.objects.all()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=list(setting.values())))
    except Setting.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))



def updateChannelSettings(request):
    channel = request.GET.get('channel')
    link = request.GET.get('link')
    try:
        # Get the profile by ID
        setting = Setting.objects.get(id=1)
        # Update the fields with new values (replace with your desired values)
        setting.channel = channel
        setting.link = link

        # Save the updated setting object
        setting.save()
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful'))
    except Setting.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Messages not found', status_code=404))


def sendToAll(request):
    try:
        message = request.GET.get('message')
        profiles = Profile.objects.all()
        for profile in profiles:
            chat_id = profile.user_id
            if request.method == 'POST':
                uploaded_image = request.FILES['image']
                path_file1 = 'img/uploads/' + uploaded_image.name
                default_storage.save(path_file1, uploaded_image)
                path_file = 'media/img/uploads/' + uploaded_image.name
                sendPhoto(chat_id=chat_id, photo=InputFile(path_file), caption=message)
            else:
                sendMessage(chat_id=chat_id, text=message)
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


def send_message(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')

    try:
        msg = Messages.objects.get(id=message_id)
        try:
            profile = Profile.objects.get(id=msg.sender_id)
            user_id = profile.user_id
            # pm1 = INIsection(Bold('پیام شما'), msg.message)
            pm2 = INIsection(Bold("جواب ادمین"), message)
            text = pm2
            sendMessage(chat_id=user_id, text=text)
            msg.answer = message
            msg.save()
            return JsonResponse(generate_response(message='successful'))
        except Profile.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))
    except Messages.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))

def send_message2(request):
    id = request.GET.get('id')
    user_id = request.GET.get('user_id')
    message = request.GET.get('message')
    print(id, user_id)
    print(message)
    if request.method == 'GET':
        try:
            # msg = Messages.objects.get(id=message_id)
            # msg.answer = message
            # msg.save()

            text = INIsection(Bold("جواب ادمین"), message)
            # sendMessage(chat_id=user_id, text=text)

        except Messages.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))


def sendTicket(request):
    lottery_id = request.GET.get('lottery_id')
    try:
        lottery = Lottery.objects.get(id=lottery_id)
        user_id = lottery.profile.user_id
        friendList = []
        friends = lottery.friends.all()
        for friend in friends:
            friendList.append(friend.enter_name)
        text = '✅ در خواست شما با موفقیت تایید شد.\nاطلاعات بلیط شما:'
        game = f' فعالیت انتخاب شده: {lottery.game.name}'
        friendList = INIsection("دوستان", friendList)
        text = text +'\n'+ game+'\n'+friendList
        name = lottery.profile.enter_name
        date = lottery.register_date
        ticket = lottery.ticket
        path_file = generate_ticket(name, date, ticket)
        sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
        lottery.payment_status = "PAID"
        lottery.status = "Registered"
        lottery.ticket_picture = path_file[len("media/"):]
        lottery.save()
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


@csrf_exempt
def sendMessageWithImage(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')
    if request.method == 'POST':
        uploaded_image = request.FILES['image']
        path_file1 = 'img/uploads/' + uploaded_image.name
        default_storage.save(path_file1, uploaded_image)
        path_file = 'media/img/uploads/' + uploaded_image.name
        try:
            msg = Messages.objects.get(id=message_id)
            try:
                profile = Profile.objects.get(id=msg.sender_id)
                user_id = profile.user_id
                # pm1 = INIsection('پیام شما', msg.message)
                pm2 = INIsection("جواب ادمین", message)
                text = pm2
                sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
                msg.answer = message
                msg.answer_picture = path_file1
                msg.save()
                return JsonResponse(generate_response(message='successful'))
            except Profile.DoesNotExist:
                return JsonResponse(generate_response(error='error in sending message'))
        except Messages.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))

        # Return success response (optional)
        return JsonResponse({'message': 'Image uploaded successfully!'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def selectToWin(request):
    lottery_id = request.GET.get('lottery_id')
    try:
        lottery = Lottery.objects.get(id=lottery_id)
        lottery.winning = True
        lottery.save()
        return JsonResponse(generate_response(message='successful'))
    except Lottery.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))

def sendMessageToWinner(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')

    try:
        profile = Profile.objects.get(id=message_id)
        user_id = profile.user_id
        text = INIsection(Bold("پیام ادمین"), message)
        sendMessage(chat_id=user_id, text=text)
        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))


@csrf_exempt
def sendMessageWithImageToWinner(request):
    message_id = request.GET.get('message_id')
    message = request.GET.get('message')
    if request.method == 'POST':
        # Access uploaded image from request.FILES
        uploaded_image = request.FILES['image']
        path_file1 = 'img/uploads/' + uploaded_image.name
        default_storage.save(path_file1, uploaded_image)
        path_file = 'media/img/uploads/' + uploaded_image.name
        try:
            profile = Profile.objects.get(id=message_id)
            user_id = profile.user_id
            text = INIsection("پیام ادمین", message)
            sendPhoto(chat_id=user_id, photo=InputFile(path_file), caption=text)
            return JsonResponse(generate_response(message='successful'))
        except Profile.DoesNotExist:
            return JsonResponse(generate_response(error='error in sending message'))
    else:
        return JsonResponse({'error': 'Invalid request method'})

import json
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django_celery_beat.models import CrontabSchedule, PeriodicTask, IntervalSchedule

def set_periodic_task_with_crontab(crontab_schedule, task_name='Scheduled Lottery Task', task_path='panel.tasks.lottery_started', args=None):
    """
    Updates or creates a PeriodicTask with the provided crontab schedule.

    Args:
        crontab_schedule (CrontabSchedule): The crontab schedule to associate with the task.
        task_name (str): The name of the periodic task. Defaults to 'Scheduled Lottery Task'.
        task_path (str): The path to the task function. Defaults to 'panel.tasks.lottery_started'.
        args (list): A list of arguments to pass to the task. Defaults to None.

    Returns:
        PeriodicTask: The updated or created PeriodicTask instance.
    """
    try:
        # Use transaction.atomic to ensure atomicity
        with transaction.atomic():
            # Convert args to JSON if provided
            args_json = json.dumps(args) if args else '[]'

            # Use get_or_create to simplify the logic
            periodic_task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    'task': task_path,
                    'crontab': crontab_schedule,
                    'args': args_json,
                }
            )

            # If the object already exists, update its fields
            if not created:
                periodic_task.crontab = crontab_schedule
                periodic_task.args = args_json
                periodic_task.save()

            return periodic_task

    except Exception as e:
        # Log the exception and re-raise it for higher-level handling
        print(f"An error occurred while setting the periodic task: {e}")
        raise


def set_crontab_schedule(minute, hour, day_of_week):
    """
    Updates or creates a CrontabSchedule entry with the provided parameters.

    Args:
        minute (str): The minute value for the crontab schedule.
        hour (str): The hour value for the crontab schedule.
        day_of_week (str): The day of the week value for the crontab schedule.

    Returns:
        CrontabSchedule: The updated or created CrontabSchedule instance.
    """
    try:
        # Use transaction.atomic to ensure atomicity
        with transaction.atomic():
            # Use get_or_create to simplify the logic
            crontab_schedule, created = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                defaults={
                    'day_of_month': '*',
                    'month_of_year': '*',
                }
            )

            # If the object already exists, update its fields
            if not created:
                crontab_schedule.minute = minute
                crontab_schedule.hour = hour
                crontab_schedule.day_of_week = day_of_week
                crontab_schedule.save()

            return crontab_schedule

    except Exception as e:
        # Log the exception and re-raise it for higher-level handling
        print(f"An error occurred while setting the crontab schedule: {e}")
        raise


def cron_day_to_number(weekday_index):
    # cron_days = {
    #     0: 6,
    #     1: 0,
    #     2: 1,
    #     3: 2,
    #     4: 3,
    #     5: 4,
    #     6: 6,
    #     7: 0
    # }

    if weekday_index == 0:
        return 6
    else:
        return weekday_index - 1


def setDate(request):
    start = json.loads(request.GET.get('start'))
    end = json.loads(request.GET.get('end'))
    lottery = json.loads(request.GET.get('lottery'))
    try:
        import datetime
        import jdatetime
        from datetime import timedelta

        # from channels.layers import get_channel_layer
        # from asgiref.sync import async_to_sync
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)('chat', {
        #     'type': 'chat_message',
        #     'message': json.dumps({
        #         'status': True,
        #     }),
        # })
        # from panel.tasks import lottery_started
        # lottery_started()

        # Convert the current datetime to Jalali datetime
        lottery_datetime = datetime.datetime.strptime(lottery, "%Y-%m-%d %H:%M")
        # Convert the input datetime to Jalali datetime
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=lottery_datetime)
        # Create a timedelta for 15 minutes before and 5 minutes after
        fifteen_minutes_before = jalali_datetime - timedelta(minutes=1)
        five_minutes_after = jalali_datetime + timedelta(minutes=1)

        setting = Setting.objects.get(id=1)
        setting.start_time = start
        setting.end_time = end
        setting.lottery_time = lottery
        setting.save()

        # Store the hour and minute, dayofweek as variables
        dayofweek = cron_day_to_number(jalali_datetime.weekday())
        hour = lottery_datetime.hour
        minute = lottery_datetime.minute
        # befor start lottery
        befor_cron = set_crontab_schedule(minute=fifteen_minutes_before.minute, hour=fifteen_minutes_before.hour, day_of_week=dayofweek)
        set_periodic_task_with_crontab(
            crontab_schedule=befor_cron,
              task_name='Scheduled Befor Lottery Task',
            task_path='panel.tasks.lottery_before_start'
        )

        # lottery time
        lottery_cron = set_crontab_schedule(minute=minute, hour=hour, day_of_week=dayofweek)
        set_periodic_task_with_crontab(
            crontab_schedule=lottery_cron,
            task_name='Scheduled Lottery Task',
            task_path='panel.tasks.lottery_started',
        )

        # after lottery
        after_cron = set_crontab_schedule(minute=five_minutes_after.minute, hour=five_minutes_after.hour, day_of_week=dayofweek)
        set_periodic_task_with_crontab(
            crontab_schedule=after_cron,
            task_name='Scheduled after Lottery Task',
            task_path='panel.tasks.lottery_ended',
        )

        return JsonResponse(generate_response(message='successful'))
    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error in sending message'))



from django.http import JsonResponse
import pandas as pd
from django.utils import timezone
from django.http import FileResponse
import os

def generateExcel(request):
    setting = Setting.objects.get(id=1)
    start_time = setting.start_time
    end_time = setting.end_time

    lotteries = Lottery.objects.filter(register_date__range=(start_time, end_time), status='Registered', payment_status='PAID')
    data = []
    for lottery in lotteries:
        data.append({
            'نام کاربری': lottery.profile.enter_id,
            'نام و نام خانوادکی': lottery.profile.enter_name,
        })
    # Creating DataFrames
    df = pd.DataFrame(data)
    # Generate a timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')

    # Create a filename with the timestamp
    filename = f'lottery_{timestamp}.xlsx'
    path_dir = 'media/excel'
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    # Writing the DataFrame to an Excel file
    df.to_excel(os.path.join(path_dir, filename), index=False, engine='openpyxl')
    # Open the file in binary mode
    file = open(os.path.join(path_dir, filename), 'rb')

    # Create a FileResponse object
    response = FileResponse(file)

    # Set the Content-Disposition header to signal the browser to download the file
    response['Content-Disposition'] = f'{filename}'

    return response


def endLottery(request):
    registered_lotteries = Lottery.objects.exclude(status='Registered')
    for lottery in registered_lotteries:
        lottery.status = 'Unregistered'
        lottery.save()

    return JsonResponse(generate_response(message='successful'))


def getPaymentsDate(request):
    try:
        lotteries = Lottery.objects.filter(payment_status='PENDING', status="Registered")
        data = []
        for lottery in list(lotteries.values()):
            l = Lottery.objects.get(pk=lottery['id'])
            lottery['register_date'] = convert_date(lottery['register_date'])
            lottery['payment_picture'] = l.payment_picture.url if l.payment_picture else None,
            # print(lottery['register_date'])
            data.append(lottery)
        # print(data)
        # Return profile data as a dictionary
        return JsonResponse(generate_response(message='successful', data=data))
    except Lottery.DoesNotExist:
        # Handle case where profile with ID is not found
        return JsonResponse(generate_response(error='Profile not found', status_code=404))


@csrf_exempt
def totalUnReadMessagesAndNewPayment(request):
    try:
        setting = Setting.objects.get(id=1)
        data = {
            'total_unread_messages': setting.total_unread_messages,
            'total_new_payments': setting.total_payments,
        }
    except Setting.DoesNotExist:
        data = {
            'total_unread_messages': 0,
            'total_new_payments': 0,
        }
    return JsonResponse(generate_response(message='successful', data=data))

def unReadMessages(request):
    id = request.GET.get('id')
    try:
        sender = Profile.objects.get(id=id)
        msg = Messages.objects.filter(sender=sender, status='OPEN')
        total_unread_messages = msg.count()
        return JsonResponse(generate_response(message='successful', data={'count': total_unread_messages}))

    except Profile.DoesNotExist:
        return JsonResponse(generate_response(error='error read total_unread_messages'))


def getParticipantsOFLottery(request):
    """
    API view to retrieve participants with specific criteria.
    """
    # Filter participants based on status, payment status, and winning status
    participants = Lottery.objects.filter(
      profile__status="Registered",
      payment_status="PAID",
      winning=False
    )
    # Prepare data for response
    data = []
    for participant in participants:
        participant_data = {
          'enter_name': participant.profile.enter_name,
          'enter_id': participant.profile.enter_id,
          'picture': participant.profile.picture.url if participant.profile.picture else None,  # Handle potential missing picture
          'ticket': participant.ticket,
          'ticket_picture': participant.ticket_picture.url if participant.ticket_picture else None,  # Handle potential missing ticket picture
        }
        data.append(participant_data)
    data = [data, len(data)]
    return JsonResponse(generate_response(data=data))


def getLotteryHistory(request):
    """
    View function to retrieve and return a list of lottery history winners.

    Returns:
        JsonResponse: A JSON response containing the list of lottery history records.
    """
    # Fetch all LotteryHistory records
    lottery_history = LotteryHistory.objects.all()
    data = []
    for lh in lottery_history:
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=lh.date)
        d = {
            'date': shamsi_date.strftime('%Y/%m/%d'),
            'winners': []
        }
        for id in lh.winners:
            l = {}
            profile = Profile.objects.get(id=id)
            l['profile_picture'] = profile.picture.url if profile.picture else None
            l['enter_name'] = profile.enter_name
            l['enter_id'] = profile.enter_id
            d['winners'].append(l)
        data.append(d)
    return JsonResponse(generate_response(data=data))