# coding: utf-8
import logging
from collections import defaultdict

from django import forms
from django.utils.translation import gettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


TELEGRAM_MAX_MESSAGE_LENGTH = 4096  # https://core.telegram.org/bots/api#sendmessage:~:text=be%20sent%2C%201%2D-,4096,-characters%20after%20entities
EVENT_TITLE_MAX_LENGTH = 500


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
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available. '
                    'If you want to specify a thread ID, separate it with "/" (e.g. "12345/12").'),
    )
    message_template = forms.CharField(
        label=_('Message template'),
        widget=forms.Textarea(attrs={'class': 'span4'}),
        help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        initial='*[Sentry]* {project_name} {tag[level]}: *{title}*\n```\n{message}```\n{url}'
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
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels also available. '
                        'If you want to specify a thread ID, separate it with "/" (e.g. "12345/12").',
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

    def compile_message_text(self, message_template: str, message_params: dict, event_message: str) -> str:
        """
        Compiles message text from template and event message.
        Truncates the original event message (`event.message`) to fit Telegram message length limit.
        """
        # TODO: add tests
        truncate_warning_text = '... (truncated)'
        truncate_warning_length = len(truncate_warning_text)

        truncated = False
        while True:
            message_text = message_template.format(**message_params, message=event_message)
            message_text_size = len(message_text)

            if truncated or message_text_size <= TELEGRAM_MAX_MESSAGE_LENGTH:
                break
            else:
                truncate_size = (message_text_size - TELEGRAM_MAX_MESSAGE_LENGTH) + truncate_warning_length
                event_message = event_message[:-truncate_size] + truncate_warning_text
                truncated = True

        return message_text

    def build_message(self, group, event):
        event_tags = defaultdict(lambda: '[NA]')
        event_tags.update({k: v for k, v in event.tags})

        message_params = {
            'title': event.title[:EVENT_TITLE_MAX_LENGTH],
            'tag': event_tags,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }
        text = self.compile_message_text(
            self.get_message_template(group.project),
            message_params,
            event.message,
        )

        return {
            'text': text,
            'parse_mode': 'Markdown',
        }

    def build_url(self, project):
        return '%s/bot%s/sendMessage' % (self.get_option('api_origin', project), self.get_option('api_token', project))

    def get_message_template(self, project):
        return self.get_option('message_template', project)

    def get_receivers(self, project) -> list[list[str, str]]:
        receivers = self.get_option('receivers', project).strip()
        if not receivers:
            return []
        return list([line.strip().split('/', maxsplit=1) for line in receivers.splitlines() if line.strip()])

    def send_message(self, url, payload, receiver: list[str, str]):
        payload['chat_id'] = receiver[0]
        if len(receiver) > 1:
            payload['message_thread_id'] = receiver[1]
        self.logger.debug('Sending message to %s' % receiver)
        response = safe_urlopen(
            method='POST',
            url=url,
            json=payload,
        )
        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))
        if response.status_code > 299:
            raise ConnectionError(response.content)

    def notify_users(self, group, event, fail_silently=False, **kwargs):
        self.logger.debug('Received notification for event: %s' % event)
        receivers = self.get_receivers(group.project)
        self.logger.debug('for receivers: %s' % ', '.join(['/'.join(item) for item in receivers] or ()))
        payload = self.build_message(group, event)
        self.logger.debug('Built payload: %s' % payload)
        url = self.build_url(group.project)
        self.logger.debug('Built url: %s' % url)
        for receiver in receivers:
            safe_execute(self.send_message, url, payload, receiver)
