# coding: utf-8
"""
Plugin for Sentry which allows sending notification via Telegram messenger.
"""
from django.conf import settings


__version__ = '0.1.2'


if settings.configured:
    from sentry.plugins import plugins, register

    from plugin import TelegramNotificationsPlugin

    if TelegramNotificationsPlugin.slug not in [plugin.slug for plugin in plugins.all()]:
        register(TelegramNotificationsPlugin)
