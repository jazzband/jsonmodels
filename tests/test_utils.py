"""Tests for utilities."""

import unittest
import re

from jsonmodels import utils


class TestCompareSchemas(unittest.TestCase):

    def test_allowed_types(self):
        """Only lists and dicts are allowed."""
        utils.compare_schemas(['one'], ['one'])
        utils.compare_schemas({'one': 'two'}, {'one': 'two'})

        self.assertRaises(
            RuntimeError, utils.compare_schemas, ('tuple',), ('tuple',))
        self.assertRaises(
            RuntimeError, utils.compare_schemas, {'this_is': 'dict'}, ['list'])

        self.assertTrue(utils.compare_schemas('string', 'string'))
        self.assertTrue(utils.compare_schemas(42, 42))
        self.assertTrue(utils.compare_schemas(23.0, 23.0))
        self.assertTrue(utils.compare_schemas(True, True))

        self.assertFalse(utils.compare_schemas('string', 'other string'))
        self.assertFalse(utils.compare_schemas(42, 1))
        self.assertFalse(utils.compare_schemas(23.0, 24.0))
        self.assertFalse(utils.compare_schemas(True, False))

    def test_basic_comparison(self):
        self.assertTrue(utils.compare_schemas({'one': 'value'}, {'one': 'value'}))
        self.assertTrue(utils.compare_schemas(['one', 'two'], ['one', 'two']))
        self.assertTrue(utils.compare_schemas(['one', 'two'], ['two', 'one']))

    def test_comparison_with_different_amount_of_items(self):
        self.assertFalse(utils.compare_schemas(
            {'one': 1, 'two': 2},
            {'one': 1, 'two': 2, 'three': 3}
        ))
        self.assertFalse(utils.compare_schemas(
            ['one', 'two'],
            ['one', 'two', 'three']
        ))

    def test_comparison_of_list_with_items_with_different_keys(self):
        self.assertTrue(utils.compare_schemas(
            [{'one': 1}, {'two': 2}],
            [{'two': 2}, {'one': 1}]
        ))


class TestRegexConvertion(unittest.TestCase):

    def test_is_ecma_regex(self):
        self.assertIs(utils.is_ecma_regex('some regex'), False)
        self.assertIs(utils.is_ecma_regex('^some regex$'), False)
        self.assertIs(utils.is_ecma_regex('/^some regex$/'), True)
        self.assertIs(utils.is_ecma_regex('/^some regex$/gim'), True)
        self.assertIs(utils.is_ecma_regex('/^some regex$/trololo'), True)

        self.assertRaises(ValueError, utils.is_ecma_regex, '/wrong regex')
        self.assertRaises(ValueError, utils.is_ecma_regex, 'wrong regex/')
        self.assertRaises(ValueError, utils.is_ecma_regex, 'wrong regex/gim')
        self.assertRaises(ValueError, utils.is_ecma_regex, 'wrong regex/asdf')
        self.assertIs(utils.is_ecma_regex('/^some regex\/gim'), True)

        self.assertIs(utils.is_ecma_regex('/^some regex\\\\/trololo'), True)
        self.assertIs(utils.is_ecma_regex('/^some regex\\\\\/gim'), True)
        self.assertIs(utils.is_ecma_regex('/\\\\/'), True)

        self.assertIs(utils.is_ecma_regex('some /regex/asdf'), False)
        self.assertIs(utils.is_ecma_regex('^some regex$//'), False)

    def test_convert_ecma_regex_to_python(self):
        self.assertEqual(
            ('some', []), utils.convert_ecma_regex_to_python('/some/'))
        self.assertEqual(
            ('some/pattern', []),
            utils.convert_ecma_regex_to_python('/some/pattern/'))
        self.assertEqual(
            ('^some \d+ pattern$', []),
            utils.convert_ecma_regex_to_python('/^some \d+ pattern$/'))

        regex, flags = utils.convert_ecma_regex_to_python('/^regex \d/i')
        self.assertEqual('^regex \d', regex)
        self.assertEqual(set([re.I]), set(flags))

        result = utils.convert_ecma_regex_to_python('/^regex \d/m')
        self.assertEqual('^regex \d', result.regex)
        self.assertEqual(set([re.M]), set(result.flags))

        result = utils.convert_ecma_regex_to_python('/^regex \d/mi')
        self.assertEqual('^regex \d', result.regex)
        self.assertEqual(set([re.M, re.I]), set(result.flags))

        self.assertRaises(
            ValueError, utils.convert_ecma_regex_to_python, '/regex/wrong')

        self.assertEqual(
            ('python regex', []),
            utils.convert_ecma_regex_to_python('python regex'))

        self.assertEqual(
            ('^another \d python regex$', []),
            utils.convert_ecma_regex_to_python('^another \d python regex$'))

        result = utils.convert_ecma_regex_to_python('python regex')
        self.assertEqual('python regex', result.regex)
        self.assertEqual([], result.flags)

    def test_convert_python_regex_to_ecma(self):
        self.assertEqual(
            '/^some regex$/',
            utils.convert_python_regex_to_ecma('^some regex$'))

        self.assertEqual(
            '/^some regex$/',
            utils.convert_python_regex_to_ecma('^some regex$', []))

        self.assertEqual(
            '/pattern \d+/i',
            utils.convert_python_regex_to_ecma('pattern \d+', [re.I]))

        self.assertEqual(
            '/pattern \d+/m',
            utils.convert_python_regex_to_ecma('pattern \d+', [re.M]))

        self.assertEqual(
            '/pattern \d+/im',
            utils.convert_python_regex_to_ecma('pattern \d+', [re.I, re.M]))

        self.assertEqual(
            '/ecma pattern$/',
            utils.convert_python_regex_to_ecma('/ecma pattern$/'))

        self.assertEqual(
            '/ecma pattern$/im',
            utils.convert_python_regex_to_ecma('/ecma pattern$/im'))

        self.assertEqual(
            '/ecma pattern$/wrong',
            utils.convert_python_regex_to_ecma('/ecma pattern$/wrong'))

        self.assertEqual(
            '/ecma pattern$/m',
            utils.convert_python_regex_to_ecma('/ecma pattern$/m'), [re.M])

    def test_converters(self):
        self.assertEqual(
            '/^ecma \d regex$/im',
            utils.convert_python_regex_to_ecma(
                *utils.convert_ecma_regex_to_python('/^ecma \d regex$/im')))

        result = utils.convert_ecma_regex_to_python(
            utils.convert_python_regex_to_ecma(
                '^some \w python regex$', [re.I]))

        self.assertEqual('^some \w python regex$', result.regex)
        self.assertEqual([re.I], result.flags)
