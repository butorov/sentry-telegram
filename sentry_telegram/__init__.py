# coding: utf-8
"""
Plugin for Sentry which allows sending notification via Telegram messenger.

DISCLAIMER: Tested only with Sentry 8.9.0
"""
from django.conf import settings


__version__ = '0.0.4'


if settings.configured:
    from sentry.plugins import register
    from .plugin import TelegramNotificationsPlugin

    register(TelegramNotificationsPlugin)
