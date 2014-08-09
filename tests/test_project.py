"""Tests for code."""

import unittest
import os
import re
import subprocess

from invoke import run

import tests

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
source_dir = os.path.join(root_dir, 'jsonmodels')
tests_dir = os.path.join(root_dir, 'tests')


def _collect_recursively(directory, result):
    for name in os.listdir(directory):
        if not re.search('^\\.', name):
            fullpath = os.path.join(directory, name)
            if re.search('\\.py$', name):
                result.append(fullpath)
            elif os.path.isdir(fullpath):
                _collect_recursively(fullpath, result)


def _collect_static(dirs):
    matches = []
    for dir_ in dirs:
        _collect_recursively(dir_, matches)
    return matches


@unittest.skipIf(tests.QUICK_TESTS, "Quick tests.")
class TestProject(unittest.TestCase):

    def test_pep257(self):
        result = []
        for filename in _collect_static([source_dir]):
            result.append(subprocess.call(['pep257', filename]))

        if any(result):
            raise RuntimeError("Tests for PEP257 compliance have failed!")

    def test_pep8_and_complexity(self):
        result = []
        for filename in _collect_static([source_dir, tests_dir]):
            result.append(subprocess.call(['flake8', filename]))

        if any(result):
            raise RuntimeError(
                "Tests for PEP8 compliance and complexity have failed!")

    @unittest.skipIf(not tests.CHECK_SPELLING, "No spelling check.")
    def test_docs(self):
            run(
                'sphinx-build -b spelling -d docs/_build/doctress '
                'docs docs/build/spelling')
