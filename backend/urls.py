"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from panel.views import *
from panel.bot import uph
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('webhook', uph, name='bot'),
    path('admin/', admin.site.urls),
    path('api/', include('panel.urls')),
    path('', home, name='panel'),
    path('Profile/', ProfileView, name='Profile'),
    path('Messages/', MessagesView, name='Messages'),
    path('Winning/', WinningView, name='Winning'),
    path('Payments/', PaymentsView, name='Payments'),
    path('Settings/', SettingsView, name='Settings'),

    path('Lottery/', LotteryView, name='Lottery'),
    path('Info/', InfoView, name='Info'),
    path('register/', register, name='register'),
    path('Login/', LoginView, name='Login'),
    path('Logout/', LogoutView, name='Logout'),

    path('password_reset/', password_reset_view, name='password_reset'),
    path('reset/', password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('paymentMessage/', paymentMessage, name='paymentMessage'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)