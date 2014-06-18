"""Tests for code."""

import unittest
import os
import re
import subprocess

from invoke import run

import tests


def _collect_recursively(directory, result):
    for name in os.listdir(directory):
        if not re.search('^\\.', name):
            fullpath = os.path.join(directory, name)
            if re.search('\\.py$', name):
                result.append(fullpath)
            elif os.path.isdir(fullpath):
                _collect_recursively(fullpath, result)


def _collect_static():
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    matches = []

    _collect_recursively(directory, matches)

    return matches


@unittest.skipIf(tests.QUICK_TESTS, "Quick tests.")
class TestProject(unittest.TestCase):

    def test_pep257(self):
        run('pep257')

    def test_pep8_and_complexity(self):
        result = []
        for filename in _collect_static():
            result.append(subprocess.call(['flake8', filename]))

        if any(result):
            raise RuntimeError('Tests for PEP8 and complexity have failed!')

    def test_docs(self):
            run(
                'sphinx-build -b spelling -d docs/_build/doctress '
                'docs docs/build/spelling')
