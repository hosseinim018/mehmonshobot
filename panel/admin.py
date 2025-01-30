from django.contrib import admin
from .models import Games, Profile, profileFriend, Lottery, Messages, Admins, Setting
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_name', 'payment_method', 'start_time', 'end_time', 'lottery_time', 'total_unread_messages', 'total_payments')
    readonly_fields = ('card_number',)  # Protect sensitive card number
    exclude = ('payment_picture', 'ticket_picture')  # Exclude image fields for now


@admin.register(Admins)
class AdminsAdmin(admin.ModelAdmin):
  list_display = ['name']
  search_fields = ['name']

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
  list_display = ['sender', 'message', 'status', 'created_at']
  list_filter = ['status']
  search_fields = ['sender__username', 'message']

@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
  list_display = ['profile', 'game', 'status', 'payment_status', 'winning']
  list_filter = ['status', 'payment_status', 'winning']
  search_fields = ['profile__username', 'game__name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  list_display = ['username', 'full_name', 'status']
  list_filter = ['status']
  search_fields = ['username', 'full_name']

@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
  list_display = ['name']
  search_fields = ['name']
