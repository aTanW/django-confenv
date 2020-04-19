#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py - python package setup
# (c) 2002,2019 Vitaly Protsko <villy@sft.ru>
# Licensed under GPLv3

from setuptools import setup

#
with open("README.rst", "r") as fh:
    README = fh.read()

#

setup(
  name='django-confenv',
  version='0.9.7',

  url='https://gihhub.com/aTanW/django-confenv',
  description='Optimized app config (+Django) from environment vars and/or files',
  long_description_content_type='text/x-rst',
  long_description=README,
  keywords=['django', 'env', 'environment', 'configuration', '12factor', 'quick', 'easy', 'config', 'env var', 'django database', 'django cache', 'django email', 'django search' ],

  author='Vitaly Protsko',
  author_email='me@protsko.expert',
  license='GPLv3',

  packages=['confenv', ],
  include_package_data=True,
  test_suite='tests.autoload',

  classifiers=[
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
  ],
)

# EOF confenv/setup.py
