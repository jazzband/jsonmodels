#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup."""

import os
import sys

import tests
from jsonmodels import __version__ as version


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# Hacking unittest.
if 'test' in sys.argv and '--quick' in sys.argv:
    tests.QUICK_TESTS = True
    del sys.argv[sys.argv.index('--quick')]

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='jsonmodels',
    version=version,
    description='Models to make easier to deal with structures'
    ' that are to be casted to JSON.',
    long_description=readme + '\n\n' + history,
    author='Szczepan Cieślik',
    author_email='szczepan.cieslik@gmail.com',
    url='https://github.com/beregond/jsonmodels',
    packages=[
        'jsonmodels',
    ],
    package_dir={'jsonmodels': 'jsonmodels'},
    include_package_data=True,
    install_requires=[
        'six',
    ],
    license="BSD",
    zip_safe=False,
    keywords='jsonmodels',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
