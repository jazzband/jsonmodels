"""Tests for code."""

import unittest

from invoke import run


class TestProject(unittest.TestCase):

    def test_pep257(self):
        run('pep257')
