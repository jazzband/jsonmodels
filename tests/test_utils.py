"""Tests for more complicated utils."""

import unittest

from .utils import compare_schemas


class TestCompareSchemas(unittest.TestCase):

    def test_allowed_types(self):
        """Only lists and dicts are allowed."""
        compare_schemas(['one'], ['one'])
        compare_schemas({'one': 'two'}, {'one': 'two'})

        self.assertRaises(
            RuntimeError, compare_schemas, ('tuple',), ('tuple',))
        self.assertRaises(
            RuntimeError, compare_schemas, {'this_is': 'dict'}, ['list'])

        self.assertTrue(compare_schemas('string', 'string'))
        self.assertTrue(compare_schemas(42, 42))
        self.assertTrue(compare_schemas(23.0, 23.0))
        self.assertTrue(compare_schemas(True, True))

        self.assertFalse(compare_schemas('string', 'other string'))
        self.assertFalse(compare_schemas(42, 1))
        self.assertFalse(compare_schemas(23.0, 24.0))
        self.assertFalse(compare_schemas(True, False))

    def test_basic_comparison(self):
        self.assertTrue(compare_schemas({'one': 'value'}, {'one': 'value'}))
        self.assertTrue(compare_schemas(['one', 'two'], ['one', 'two']))
        self.assertTrue(compare_schemas(['one', 'two'], ['two', 'one']))

    def test_comparison_with_different_amount_of_items(self):
        self.assertFalse(compare_schemas(
            {'one': 1, 'two': 2},
            {'one': 1, 'two': 2, 'three': 3}
        ))
        self.assertFalse(compare_schemas(
            ['one', 'two'],
            ['one', 'two', 'three']
        ))
