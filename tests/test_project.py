import os
import re
import subprocess

import pytest
from invoke import run

import tests

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
source_dir = os.path.join(root_dir, "jsonmodels")
tests_dir = os.path.join(root_dir, "tests")


@pytest.mark.skipif(not tests.LINT, reason="No lint tests.")
def test_pep8_and_complexity():
    result = []
    for filename in _collect_static([source_dir, tests_dir]):
        result.append(subprocess.call(["flake8", filename]))

    if any(result):
        raise RuntimeError("Tests for PEP8 compliance and complexity have failed!")


@pytest.mark.skipif(
    not tests.LINT or not tests.CHECK_SPELLING, reason="No spelling check."
)
def test_docs():
    run("sphinx-build -b spelling -d docs/_build/doctress docs docs/build/spelling")


def _collect_static(dirs):
    matches = []
    for dir_ in dirs:
        _collect_recursively(dir_, matches)
    return matches


def _collect_recursively(directory, result):
    for name in os.listdir(directory):
        if not re.search("^\\.", name):
            fullpath = os.path.join(directory, name)
            if re.search("\\.py$", name):
                result.append(fullpath)
            elif os.path.isdir(fullpath):
                _collect_recursively(fullpath, result)
