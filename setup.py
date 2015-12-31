#!/usr/bin/env python
# coding: utf-8
import os
import sys

from setuptools.command.test import test as TestCommand
from jsonmodels import __version__, __author__, __email__

from setuptools import setup


PROJECT_NAME = 'jsonmodels'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--cov', PROJECT_NAME]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Hacking tests.
try:
    import tests
except ImportError:
    pass
else:
    if 'test' in sys.argv and '--no-lint' in sys.argv:
        tests.LINT = False
        del sys.argv[sys.argv.index('--no-lint')]

    if 'test' in sys.argv and '--spelling' in sys.argv:
        tests.CHECK_SPELLING = True
        del sys.argv[sys.argv.index('--spelling')]

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name=PROJECT_NAME,
    version=__version__,
    description='Models to make easier to deal with structures that'
    ' are converted to, or read from JSON.',
    long_description=readme + '\n\n' + history,
    author=__author__,
    author_email=__email__,
    url='https://github.com/beregond/jsonmodels',
    packages=[
        PROJECT_NAME,
    ],
    package_dir={PROJECT_NAME: PROJECT_NAME},
    include_package_data=True,
    install_requires=[
        'python-dateutil',
        'six',
    ],
    license="BSD",
    zip_safe=False,
    keywords=PROJECT_NAME,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    cmdclass={
        'test': PyTest,
    },
)
