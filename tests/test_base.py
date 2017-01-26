# coding: utf-8
from sentry.plugins import plugins
from sentry.testutils import PluginTestCase

from sentry_telegram import TelegramNotificationsPlugin


class BaseTest(PluginTestCase):
    plugin = TelegramNotificationsPlugin

    def test_is_registered(self):
        assert plugins.get('sentry_telegram').slug == self.plugin.slug
