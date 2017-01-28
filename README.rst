Sentry Telegram |travis| |codecov| |pypi|
=========================================

Plugin for Sentry which allows sending notification via `Telegram <https://telegram.org/>`_ messenger.

    **DISCLAIMER**: Tested only with Sentry 8.9.0

    Sentry API under development and `is not frozen <https://docs.sentry.io/server/plugins/>`_.


Installation
------------

1. Install this package

.. code-block:: bash

    pip install sentry-telegram

2. Add plugin to ``INSTALLED_APPS`` of Sentry

.. code-block:: python

    INSTALLED_APPS = INSTALLED_APPS + ['sentry_telegram']

3. Restart your Sentry.
4. Go to your Sentry web interface. On ``Settings`` page of one of your project.
5. On ``Integrations`` page find ``Telegram Notifications`` plugin and enable it.
6. On ``Configure plugin`` page and configure plugin.

   See `Telegram's documentation <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_ to know how create ``BotAPI Token``.

7. Done!

.. |travis| image:: https://travis-ci.org/butorov/sentry-telegram.svg?branch=master
   :target: https://travis-ci.org/butorov/sentry-telegram
   :alt: Build Status

.. |codecov| image:: https://codecov.io/gh/butorov/sentry-telegram/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/butorov/sentry-telegram?branch=master
   :alt: Coverage Status

.. |pypi| image:: https://badge.fury.io/py/sentry-telegram.svg
   :target: https://badge.fury.io/py/sentry-telegram
