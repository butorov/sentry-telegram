# coding: utf-8
"""
Plugin for Sentry which allows sending notification via Telegram messenger.
"""
try:
    from django.conf import settings
except ImportError:
    settings = None


__version__ = '0.3.0'


if settings is not None and settings.configured:
    from sentry.plugins import plugins, register

    from plugin import TelegramNotificationsPlugin

    if TelegramNotificationsPlugin.slug not in [plugin.slug for plugin in plugins.all()]:
        register(TelegramNotificationsPlugin)
