Sentry Telegram |travis| |codecov| |pypi|
=========================================

Plugin for Sentry which allows sending notification via `Telegram <https://telegram.org/>`_ messenger.

Presented plugin tested with Sentry from 8.9 to 9.1.1.

    **DISCLAIMER**: Sentry API is under development and `is not frozen <https://docs.sentry.io/server/plugins/>`_.


How will it look like
---------------------

.. image:: https://raw.githubusercontent.com/butorov/sentry-telegram/master/docs/images/telegram-window.png
   :target: https://github.com/butorov/sentry-telegram/blob/master/docs/images/telegram-window.png
   :alt: How will it look like

Installation
------------

1. Install this package

.. code-block:: bash

    pip install sentry-telegram

2. Go to your Sentry root/sentry/
3. Open requirements.txt and include new plugin in it

.. code-block:: bash

    # Add plugins here
    sentry-telegram

4. Set cd to your Sentry root in console, write this to rebuild your docker

.. code-block:: bash

    docker-compose down
    docker-compose up -d --build
    
    
5. Go to your Sentry web interface. Open ``Settings`` page of one of your projects.
6. On ``Integrations`` (or ``Legacy Integrations``) page, find ``Telegram Notifications`` plugin and enable it.
7. Configure plugin on ``Configure plugin`` page.

   See `Telegram's documentation <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_ to know how to create ``BotAPI Token``.

8. Don't forget to specify Alerts rules for errors in your project settings, in web panel.
9. Done!

.. |travis| image:: https://travis-ci.org/butorov/sentry-telegram.svg?branch=master
   :target: https://travis-ci.org/butorov/sentry-telegram
   :alt: Build Status

.. |codecov| image:: https://codecov.io/gh/butorov/sentry-telegram/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/butorov/sentry-telegram?branch=master
   :alt: Coverage Status

.. |pypi| image:: https://badge.fury.io/py/sentry-telegram.svg
   :target: https://pypi.python.org/pypi/sentry-telegram
