# coding: utf-8
from mock import patch
import pytest

import sentry
from sentry.plugins import plugins, Notification
from sentry.testutils import PluginTestCase
from sentry.utils.samples import create_sample_event


from sentry_telegram import TelegramNotificationsPlugin


class BaseTest(PluginTestCase):
    plugin = TelegramNotificationsPlugin

    def setUp(self):
        super(BaseTest, self).setUp()
        self.initialized_plugin = self.plugin()

    def test_is_registered(self):
        assert plugins.get('sentry_telegram').slug == self.plugin.slug

    @pytest.mark.skipif(not sentry.__version__.startswith('8.9.0'), reason="sentry versions newer than 8.9.0 message text is longer than title")
    def test_old_complex_send_notification(self):
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        self.initialized_plugin.set_option('message_template',
                                           '*[Sentry]* {project_name} {tag[level]}: {title}\n{message}\n{url}',
                                           self.project)
        event = create_sample_event(self.project, platform='python')
        notification = Notification(event=event)
        with patch('requests.sessions.Session.request') as request:
            self.initialized_plugin.notify(notification)
            assert request.assert_called_once_with(
                allow_redirects=False,
                method='POST',
                headers={'Content-Type': 'application/json'},
                url=u'https://api.telegram.org/botapi:token/sendMessage',
                json={'text': u'*[Sentry]* Bar error: This is an example python exception\nThis is an example python exception\nhttp://testserver/baz/bar/issues/1/', 'parse_mode': 'Markdown', 'chat_id': '123'},
                timeout=30,
                verify=True,
            )

    @pytest.mark.skipif(sentry.__version__.startswith('8.9.0'), reason="sentry 8.9.0 message text equals to title")
    def test_complex_send_notification(self):
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        self.initialized_plugin.set_option('message_template',
                                           '*[Sentry]* {project_name} {tag[level]}: {title}\n{message}\n{url}',
                                           self.project)
        event = create_sample_event(self.project, platform='python')
        notification = Notification(event=event)
        with patch('requests.sessions.Session.request') as request:
            self.initialized_plugin.notify(notification)
            assert request.call_count == 1
            assert request.call_args_list[0][1] == dict(
                allow_redirects=False,
                method='POST',
                headers={'Content-Type': 'application/json'},
                url=u'https://api.telegram.org/botapi:token/sendMessage',
                json={
                    'text': u'*[Sentry]* Bar error: This is an example python exception\nThis is an example python exception raven.scripts.runner in main\nhttp://testserver/baz/bar/issues/1/',
                    'parse_mode': 'Markdown', 'chat_id': '123'},
                timeout=30,
                verify=True,
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
