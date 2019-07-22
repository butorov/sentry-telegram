# coding: utf-8
import logging
from collections import defaultdict

from django import forms
from django.utils.translation import ugettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen, SafeSession
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    api_origin = forms.CharField(
        label=_('Telegram API origin'),
        widget=forms.TextInput(attrs={'placeholder': 'https://api.telegram.org'}),
        initial='https://api.telegram.org'
    )
    api_token = forms.CharField(
        label=_('BotAPI token'),
        widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    )
    proxy = forms.CharField(
        label=_('Proxy URL'),
        widget=forms.TextInput(attrs={'placeholder': 'socks5://username:password@example.org:8080'})
    )
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available.'))

    message_template = forms.CharField(
        label=_('Message template'),
        widget=forms.Textarea(attrs={'class': 'span4'}),
        help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        initial='*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
    )


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
                'name': 'api_origin',
                'label': 'Telegram API origin',
                'type': 'text',
                'placeholder': 'https://api.telegram.org',
                'validators': [],
                'required': True,
                'default': 'https://api.telegram.org'
            },
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
                'name': 'proxy',
                'label': 'Proxy URL',
                'type': 'text',
                'placeholder': 'socks5://username:password@example.org:8080',
                'validators': [],
                'required': False,
            },
            {
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels also available.',
                'validators': [],
                'required': True,
            },
            {
                'name': 'message_template',
                'label': 'Message Template',
                'type': 'textarea',
                'help': 'Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}. Undefined tags will be shown as [NA]',
                'validators': [],
                'required': True,
                'default': '*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
            },
        ]

    def build_message(self, group, event):
        the_tags = defaultdict(lambda: '[NA]')
        the_tags.update({k:v for k, v in event.tags})
        names = {
            'title': event.title,
            'tag': the_tags,
            'message': event.message,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }

        template = self.get_message_template(group.project)

        text = template.format(**names)

        return {
            'text': text,
            'parse_mode': 'Markdown',
        }

    def build_url(self, project):
        return '%s/bot%s/sendMessage' % (self.get_option('api_origin', project), self.get_option('api_token', project))

    def get_message_template(self, project):
        return self.get_option('message_template', project)

    def get_receivers(self, project):
        receivers = self.get_option('receivers', project)
        if not receivers:
            return []
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

    def send_message_via_proxy(self, url, payload, receiver, proxy):
        payload['chat_id'] = receiver
        self.logger.debug('Sending message to %s ' % receiver)

        # safe_urlopen has no proxies option yet
        # below is same as safe_urlopen, but wrote manually (and with proxies)

        headers = {}
        headers.setdefault('Content-Type', 'application/json')

        proxies = {
            'http': proxy,
            'https': proxy
        }

        session = SafeSession()
        response = session.request(
            method='POST',
            url=url,
            allow_redirects=False,
            timeout=30,
            verify=True,
            json=payload,
            headers=headers,
            proxies=proxies
        )

        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))

    def notify_users(self, group, event, fail_silently=False, **kwargs):
        self.logger.debug('Received notification for event: %s' % event)
        receivers = self.get_receivers(group.project)
        self.logger.debug('for receivers: %s' % ', '.join(receivers or ()))
        payload = self.build_message(group, event)
        self.logger.debug('Built payload: %s' % payload)
        url = self.build_url(group.project)
        self.logger.debug('Built url: %s' % url)
        proxy = self.get_option('proxy', group.project)
        self.logger.debug('Proxy url: %s', proxy)
        for receiver in receivers:
            if not proxy :
                safe_execute(self.send_message, url, payload, receiver, _with_transaction=False)
            else:
                safe_execute(self.send_message_via_proxy, url, payload, receiver, proxy, _with_transaction=False)
