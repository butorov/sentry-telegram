# coding: utf-8
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    api_token = forms.CharField(
        label=_('BotAPI token'),
        widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    )
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available.'))


class TelegramNotificationsPlugin(notify.NotificationPlugin):
    title = 'Telegram Notifications'
    slug = 'sentry_telegram'
    description = package_doc
    version = __version__
    author = 'Viacheslav Butorov'
    author_url = 'https://github.com/butorov/sentry-telegram'
    resource_links = [
        ('Bug Tracker', 'https://github.com/butorov/sentry-telegram/issues'),
        ('Source', 'https://github.com/butorov/sentry-telegram'),
    ]

    conf_key = 'sentry_telegram'
    conf_title = title

    project_conf_form = TelegramNotificationsOptionsForm

    logger = logging.getLogger('sentry.plugins.sentry_telegram')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('api_token', project) and self.get_option('receivers', project))

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'api_token',
                'label': 'BotAPI token',
                'type': 'text',
                'help': 'Read more: https://core.telegram.org/bots/api#authorizing-your-bot',
                'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                'validators': [],
                'required': True,
            },
            {
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels also available.',
                'validators': [],
                'required': True,
            },
        ]

    def build_message(self, activity):
        group = activity.group
        text = '*[Sentry]* {project_name} {level}\n{url}'.format(**{
            'project_name': group.project.name,
            'level': activity.type,
            'url': group.get_absolute_url(),
        })
        return {
            'text': text,
            'parse_mode': 'Markdown',
        }

    def build_url(self, project):
        return 'https://api.telegram.org/bot%s/sendMessage' % self.get_option('api_token', project)

    def get_receivers(self, project):
        receivers = self.get_option('receivers', project)
        if not receivers:
            return ()
        return filter(bool, receivers.strip().splitlines())

    def send_message(self, url, payload, receiver):
        payload['chat_id'] = receiver
        self.logger.debug('Sending message to %s ' % receiver)
        response = safe_urlopen(
            method='POST',
            url=url,
            json=payload,
        )
        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))

    def notify_about_activity(self, activity):
        self.logger.debug('Received notification for activity: %s' % activity)
        receivers = self.get_receivers(activity.project)
        self.logger.debug('for receivers: %s' % receivers)
        payload = self.build_message(activity)
        self.logger.debug('Built payload: %s' % payload)
        url = self.build_url(activity.project)
        self.logger.debug('Built url: %s' % url)
        for receiver in receivers:
            safe_execute(self.send_message, url, payload, receiver, _with_transaction=False)
