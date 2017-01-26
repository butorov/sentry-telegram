# coding: utf-8
import os


os.environ.setdefault('DB', 'sqlite')
pytest_plugins = [
    'sentry.utils.pytest',
]
