# Sentry Telegram ![Build Status](https://travis-ci.org/butorov/sentry-telegram.svg?branch=master) ![Coverage Status](https://codecov.io/gh/butorov/sentry-telegram/branch/master/graph/badge.svg) ![PyPI](https://badge.fury.io/py/sentry-telegram.svg) ![PyPI - Downloads](https://img.shields.io/pypi/dm/sentry-telegram)

Plugin for Sentry which allows sending notifications via the [Telegram](https://telegram.org/) messenger.

As any plugins installation is only available for [self-hosted Sentry](https://github.com/getsentry/self-hosted) instances, this plugin is unavailable for cloud-hosted [Sentry](https://sentry.io/).

The plugin has been tested with the most recent version of Sentry available at the time - 24.5.x.

# Features

- Sending notifications about issues to one or many Telegram users and/or groups.
- Sending notifications to particular threads (Topics) in chats.
- Customizable message template with placeholders for the project name, issue URL, title, error message, and tags.
- Support for Markdown formatting in the message template.
- Proxy support (through `origin_url` parameter in the configuration, see [#20](https://github.com/butorov/sentry-telegram/issues/20#issuecomment-483024745)).

# How will it look

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/docs/images/telegram-window-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/docs/images/telegram-window-light.png">
  <img alt="How will it look" src="/docs/images/telegram-window-light.png">
</picture>

# Compatible versions

> **DISCLAIMER**: Sentry API is under development and is not frozen.
> I'm trying to keep up with the latest changes, but I can't guarantee compatibility with every version of Sentry. 
> If you have any issues, please create an [issue on GitHub](https://github.com/butorov/sentry-telegram/issues).

Table of compatibility:

| Plugin version | Compatible Sentry versions | Tested in Sentry versions                           |
|----------------|----------------------------|-----------------------------------------------------|
| 0.5.0          | 24.4.x to 24.5.x           | 24.4.1, 24.4.2, 24.5.0                              |
| 0.4.0          | 8.x to 9.x                 | 8.9, 9.1.1                                          |
| 0.3.0          | 8.x to 9.x                 | 8.21, 8.22, 9.0.0, 9.1.0                            |
| 0.2.2          | 8.x to 9.x                 | 8.21, 8.22, 9.0.0                                   |
| 0.2.1          | 8.x to 9.x                 | 8.21, 8.22, 9.0.0                                   |
| 0.2.0          | 8.x                        | 8.9, 8.10, 8.11, 8.12, 8.13, 8.14, 8.15, 8.16, 8.17 |
| 0.1.2          | 8.x                        | 8.9.0, 8.12.0                                       |
| 0.1.1          | 8.x                        | 8.9.0                                               |


# Installation

> [!TIP]
> You can initiate the plugin installation both before and after setting up a Sentry instance.

1. On the host machine, where you have the [self-hosted Sentry repository](https://github.com/getsentry/self-hosted) cloned,
   copy `sentry/enhance-image.example.sh` file to `sentry/enhance-image.sh`:
   ```bash
   cp sentry/enhance-image.example.sh sentry/enhance-image.sh
   ```
2. Open `sentry/enhance-image.sh` file in your favorite text editor and add the following line to the end of the file:
   ```bash
   pip install sentry-telegram
   ```
   
   Or apply this command:
   ```bash
    echo "pip install sentry-telegram" >> sentry/enhance-image.sh
    ```
   
   So, the file will look like:
   ```bash
   #!/bin/bash
   # Enhance the base $SENTRY_IMAGE with additional dependencies, plugins - see https://github.com/getsentry/self-hosted#enhance-sentry-image
   # For example:
   # apt-get update
   # apt-get install -y gcc libsasl2-dev python-dev libldap2-dev libssl-dev
   # pip install python-ldap
   
   pip install sentry-telegram
   ```
   
   If you want to install a specific version of the plugin, you can specify it in the command (for example, version 0.5.0):
   ```bash
   echo "pip install sentry-telegram==0.5.0" >> sentry/enhance-image.sh
   ```
3. Run `./install.sh` script to build the Sentry image with the plugin installed:
   ```bash
   ./install.sh
   ```
4. After the script finishes, you can start the Sentry instance, or if it was already running, restart it.
   - For the first start, you need to run the following command:
     ```bash
     docker compose up -d
     ```
   - If the Sentry instance was already running, it's enough to restart several services:
     ```bash
     docker compose restart web worker cron sentry-cleanup
     ```

# Configuration

## Adding the plugin to a project

### From the Organization Settings

1. Go to your Sentry web interface. Open Settings page, that located in the left sidebar (`<your-sentry-installation-url>/settings/sentry/`).
2. In the "Organization" section of the second sidebar, go to the "Integrations" page (`<your-sentry-installation-url>/settings/sentry/integrations/`).
3. Find the "Telegram Notifications" plugin in the list of integrations and click on it.
4. Press the "Add to Project" button. You will be prompted to select a project to which you want to add the plugin (unless you have only one project).
5. You will be redirected to the plugin configuration page for the selected project.

### From the Project Settings

1. Go to your Sentry web interface. Open the Settings page of one of your projects (`<your-sentry-installation-url>/settings/sentry/projects/<project-name>/`).
2. In the second sidebar, go to the "Legacy Integrations" section (`<your-sentry-installation-url>/settings/sentry/projects/<project-name>/plugins/`).
3. Find the "Telegram Notifications" plugin in the list of integrations and select the "Configure plugin" link at the bottom of the plugin card.
4. Press the "Enable Plugin" button.

## Configuring the plugin

0. Assume you are on the plugin configuration page.
1. You need to create a Telegram bot to get the Bot API token. To do this, you need to talk to the [BotFather in Telegram](https://t.me/botfather).
   You can find more detailed instructions on how to create a bot in the [official Telegram documentation](https://core.telegram.org/bots/features#creating-a-new-bot).
2. After you have created a bot, copy the Bot API token and paste it into the "Bot API token" field on the plugin configuration page.
3. In the Receivers field, you need to specify the list of Telegram users and/or groups that will receive notifications.
   You can specify multiple receivers, each on a new line. You can use user/chat IDs, **but not usernames**.
   - To obtain the user ID, use can use one of the bots that can provide you with your user ID.
     For example, [this one](https://t.me/getmyid_bot) or [this one](https://t.me/raw_data_bot) (I don't have any relation to these bots) or any other, which you trust.
     Of course, you can use your own Bot API token to obtain the user ID.
   - To obtain the chat ID the easies way is to use "Share" button in the Telegram app and get the chat ID from the link.
     For example, if you share the chat with yourself, you will get the link like `https://t.me/c/123456789`.
     The chat ID in this case is `-123456789`.
     According to the Telegram Bot API requirements, you need to specify the chat ID with the minus sign (`-`) at the beginning.
   - If you have a chat with Topics, you can get the chat ID from the link as well. You need to share the particular Topic.
     For example, if you got a link `https://t.me/c/123456789/5`, the chat ID is `123456789` and the Topic ID is `5`.
     The receiver in this case will be `-123456789/5`.
   - Don't forget that all the receivers should allow the bot to send messages to them. 
     - For personal chats, it's enough to start a chat with the bot.
     - For groups, the bot should be added to the group and have a permission to send messages.
4. Set the "Message Template" as you want, or start with the default one.
   You can use the following placeholders in the message template:
   - `{project_name}` - the name of the project where the issue occurred.
   - `{url}` - the URL to the issue in the Sentry web interface.
   - `{title}` - the title of the issue.
   - `{message}` - the error message of the issue.
   - `tag[<tag_name>]` - the value of the tag with the name `<tag_name>`. For example, `tag[level]`. If the tag is not found, the placeholder will be replaced with `[NA]`.

   Note that the Telegram message will be sent in Markdown format, so you can use Markdown formatting in the message template.
5. Press the "Save Changes" button.
6. Now you can test the plugin by pressing the "Test Plugin" button. You should receive a test message in the Telegram chat(s).
7. If you received the test message to Telegram and got `Test Results "No errors returned"` message at the top of the plugin configuration page, you are all set up! 

> [!TIP]
> Don't forget to check the Sentry's alert rules to make sure that the Sentry will send notifications
for the events you want (new issues only, or all issues, etc.).

# Support This Project

If you find this project useful and would like to contribute financially, you can find several ways to do so on my [GitHub Sponsors page](https://github.com/sponsors/butorov).
Your support will assist in covering the costs of the servers used for testing the plugin and will serve as motivation for further improvements.

Your support is highly appreciated!
