import os
import re
import subprocess

import pytest
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


@pytest.mark.skipif(tests.QUICK_TESTS, reason="Quick tests.")
def test_pep8_and_complexity():
    result = []
    for filename in _collect_static([source_dir, tests_dir]):
        result.append(subprocess.call(['flake8', filename]))

    if any(result):
        raise RuntimeError(
            "Tests for PEP8 compliance and complexity have failed!")


@pytest.mark.skipif(
    tests.QUICK_TESTS or not tests.CHECK_SPELLING, reason="No spelling check.")
def test_docs():
        run(
            'sphinx-build -b spelling -d docs/_build/doctress '
            'docs docs/build/spelling')


def test_jsonmodels_module_coverage_by_dirty_hack():
    """Trick `pytest-cov` plugin and reimport `jsonmodels` module.

    Problem with `pytest-cov` plugin is that `jsonmodels` module is already
    imported when plugin start his work, thats why it will never know this
    module is used (since it won't be imported, because it already sits in
    memory).

    This have a simple solution - don't use `pytest-cov`, but pure `coverage`
    library to run your tests. You can find dirty hack below which allows NOT
    do that. Why? If coverage is made always during test (and when calling
    `setup.py test`) it is much more easier to maintain this code, so thanks to
    that hack below we can integrate this plugin fully.

    It's worth it, IMHO.

    """
    import sys
    del sys.modules['jsonmodels']
    import jsonmodels

    assert jsonmodels.__version__
