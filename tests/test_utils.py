"""Tests for more complicated utils."""

import unittest

from .utils import compare_schemes


class TestCompareSchemes(unittest.TestCase):

    def test_allowed_types(self):
        """Only lists and dicts are allowed."""
        compare_schemes(['one'], ['one'])
        compare_schemes({'one': 'two'}, {'one': 'two'})

        self.assertRaises(
            RuntimeError, compare_schemes, ('tuple',), ('tuple',))
        self.assertRaises(
            RuntimeError, compare_schemes, {'this_is': 'dict'}, ['list'])

        self.assertTrue(compare_schemes('string', 'string'))
        self.assertTrue(compare_schemes(42, 42))
        self.assertTrue(compare_schemes(23.0, 23.0))
        self.assertTrue(compare_schemes(True, True))

        self.assertFalse(compare_schemes('string', 'other string'))
        self.assertFalse(compare_schemes(42, 1))
        self.assertFalse(compare_schemes(23.0, 24.0))
        self.assertFalse(compare_schemes(True, False))

    def test_basic_comparison(self):
        self.assertTrue(compare_schemes({'one': 'value'}, {'one': 'value'}))
        self.assertTrue(compare_schemes(['one', 'two'], ['one', 'two']))
        self.assertTrue(compare_schemes(['one', 'two'], ['two', 'one']))
