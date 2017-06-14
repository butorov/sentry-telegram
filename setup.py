#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

import sentry_telegram


setup(
    name='sentry_telegram',
    version=sentry_telegram.__version__,
    packages=['sentry_telegram'],
    url='https://github.com/butorov/sentry-telegram',
    author='Viacheslav Butorov',
    author_email='butorovv@gmail.com',
    description='Plugin for Sentry which allows sending notification via Telegram messenger.',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    include_package_data=True,
)
