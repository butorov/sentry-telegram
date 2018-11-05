# coding: utf-8
from mock import patch
from distutils.version import LooseVersion as V

import pytest

import sentry
from sentry.plugins import plugins, Notification
from sentry.testutils import PluginTestCase
from sentry.utils.samples import create_sample_event


from sentry_telegram import TelegramNotificationsPlugin


sentry_version = V(sentry.__version__)


class BaseTest(PluginTestCase):
    plugin = TelegramNotificationsPlugin

    def setUp(self):
        super(BaseTest, self).setUp()
        self.initialized_plugin = self.plugin()

    def test_is_registered(self):
        assert plugins.get('sentry_telegram').slug == self.plugin.slug

    def send_notification_helper(self):
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        self.initialized_plugin.set_option(
            'message_template',
            '*[Sentry]* {project_name} {tag[level]}: {title}\n{message}\n{url}',
            self.project,
        )
        event = create_sample_event(self.project, platform=self.get_test_platform_name())
        notification = Notification(event=event)
        with patch('requests.sessions.Session.request') as request:
            self.initialized_plugin.notify(notification)
            return request

    @staticmethod
    def get_test_platform_name():
        if sentry_version < V('9'):
            return 'python'
        else:
            return 'Python'

    @staticmethod
    def assert_notification_helper(request_call, message_text):
        assert request_call == dict(
            allow_redirects=False,
            method='POST',
            headers={'Content-Type': 'application/json'},
            url='https://api.telegram.org/botapi:token/sendMessage',
            json={
                'text': message_text,
                'parse_mode': 'Markdown',
                'chat_id': '123',
            },
            timeout=30,
            verify=True,
        )

    @pytest.mark.skipif(sentry_version > V('8.9.0'), reason='sentry versions newer than 8.9.0 message text is longer than title')
    def test_old_complex_send_notification(self):
        request = self.send_notification_helper()
        self.assert_notification_helper(
            request.call_args_list[0][1],
            '*[Sentry]* Bar error: This is an example python exception\nThis is an example python exception\nhttp://testserver/baz/bar/issues/1/',
        )

    @pytest.mark.skipif(V('8.19.0') < sentry_version or sentry_version <= V('8.9.0'), reason='sentry 8.9.0 message text equals to title')
    def test_complex_send_notification_9_19(self):
        request = self.send_notification_helper()
        assert request.call_count == 1
        self.assert_notification_helper(
            request.call_args_list[0][1],
            '*[Sentry]* Bar error: This is an example python exception\nThis is an example python exception raven.scripts.runner in main\nhttp://testserver/baz/bar/issues/1/',
        )

    @pytest.mark.skipif(sentry_version < V('8.20.0'), reason='sentry 8.9.0 message text equals to title')
    def test_complex_send_notification(self):
        request = self.send_notification_helper()
        assert request.call_count == 1
        self.assert_notification_helper(
            request.call_args_list[0][1],
            '*[Sentry]* Bar error: This is an example Python exception\nThis is an example Python exception raven.scripts.runner in main\nhttp://testserver/baz/bar/issues/1/',
        )

    def test_get_empty_receivers_list(self):
        self.initialized_plugin.set_option('receivers', '', self.project)
        assert self.initialized_plugin.get_receivers(self.project) == []

    def test_get_config(self):
        self.initialized_plugin.get_config(self.project)

    def test_is_configured(self):
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        assert self.initialized_plugin.is_configured(self.project)

    def test_is_not_configured(self):
        assert not self.initialized_plugin.is_configured(self.project)
