#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

import sentry_telegram

requirements = [
    'sentry==8.9.0',
]


setup(
    name='sentry_telegram',
    version=sentry_telegram.__version__,
    packages=['sentry_telegram'],
    url='https://github.com/butorov/sentry-telegram',
    author='Viacheslav Butorov',
    author_email='butorovv@gmail.com',
    description=sentry_telegram.__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    include_package_data=True,
    install_requires=requirements,
)
