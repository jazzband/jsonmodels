import re

import pytest

from jsonmodels import utils


def test_allowed_types():
    """Only lists and dicts are allowed."""
    utils.compare_schemas(['one'], ['one'])
    utils.compare_schemas({'one': 'two'}, {'one': 'two'})

    with pytest.raises(RuntimeError):
        utils.compare_schemas(('tuple',), ('tuple',))

    with pytest.raises(RuntimeError):
        utils.compare_schemas({'this_is': 'dict'}, ['list'])

    assert utils.compare_schemas('string', 'string')
    assert utils.compare_schemas(42, 42)
    assert utils.compare_schemas(23.0, 23.0)
    assert utils.compare_schemas(True, True)

    assert not utils.compare_schemas('string', 'other string')
    assert not utils.compare_schemas(42, 1)
    assert not utils.compare_schemas(23.0, 24.0)
    assert not utils.compare_schemas(True, False)


def test_basic_comparison():
    assert utils.compare_schemas({'one': 'value'}, {'one': 'value'})
    assert utils.compare_schemas(['one', 'two'], ['one', 'two'])
    assert utils.compare_schemas(['one', 'two'], ['two', 'one'])


def test_comparison_with_different_amount_of_items():
    assert not utils.compare_schemas(
        {'one': 1, 'two': 2},
        {'one': 1, 'two': 2, 'three': 3}
    )
    assert not utils.compare_schemas(
        ['one', 'two'],
        ['one', 'two', 'three']
    )


def test_comparison_of_list_with_items_with_different_keys():
    assert utils.compare_schemas(
        [{'one': 1}, {'two': 2}],
        [{'two': 2}, {'one': 1}]
    )


def test_is_ecma_regex():
    assert utils.is_ecma_regex('some regex') is False
    assert utils.is_ecma_regex('^some regex$') is False
    assert utils.is_ecma_regex('/^some regex$/') is True
    assert utils.is_ecma_regex('/^some regex$/gim') is True
    assert utils.is_ecma_regex('/^some regex$/trololo') is True

    with pytest.raises(ValueError):
        utils.is_ecma_regex('/wrong regex')
    with pytest.raises(ValueError):
        utils.is_ecma_regex('wrong regex/')
    with pytest.raises(ValueError):
        utils.is_ecma_regex('wrong regex/gim')
    with pytest.raises(ValueError):
        utils.is_ecma_regex('wrong regex/asdf')

    assert utils.is_ecma_regex('/^some regex\/gim') is True

    assert utils.is_ecma_regex('/^some regex\\\\/trololo') is True
    assert utils.is_ecma_regex('/^some regex\\\\\/gim') is True
    assert utils.is_ecma_regex('/\\\\/') is True

    assert utils.is_ecma_regex('some /regex/asdf') is False
    assert utils.is_ecma_regex('^some regex$//') is False


def test_convert_ecma_regex_to_python():
    assert ('some', []) == utils.convert_ecma_regex_to_python('/some/')
    assert (
        ('some/pattern', []) ==
        utils.convert_ecma_regex_to_python('/some/pattern/')
    )
    assert (
        ('^some \d+ pattern$', []) ==
        utils.convert_ecma_regex_to_python('/^some \d+ pattern$/')
    )

    regex, flags = utils.convert_ecma_regex_to_python('/^regex \d/i')
    assert '^regex \d' == regex
    assert set([re.I]) == set(flags)

    result = utils.convert_ecma_regex_to_python('/^regex \d/m')
    assert '^regex \d' == result.regex
    assert set([re.M]) == set(result.flags)

    result = utils.convert_ecma_regex_to_python('/^regex \d/mi')
    assert '^regex \d' == result.regex
    assert set([re.M, re.I]) == set(result.flags)

    with pytest.raises(ValueError):
        utils.convert_ecma_regex_to_python('/regex/wrong')

    assert (
        ('python regex', []) ==
        utils.convert_ecma_regex_to_python('python regex')
    )

    assert (
        ('^another \d python regex$', []) ==
        utils.convert_ecma_regex_to_python('^another \d python regex$')
    )

    result = utils.convert_ecma_regex_to_python('python regex')
    assert 'python regex' == result.regex
    assert [] == result.flags


def test_convert_python_regex_to_ecma():
    assert (
        '/^some regex$/' ==
        utils.convert_python_regex_to_ecma('^some regex$')
    )

    assert (
        '/^some regex$/' ==
        utils.convert_python_regex_to_ecma('^some regex$', [])
    )

    assert (
        '/pattern \d+/i' ==
        utils.convert_python_regex_to_ecma('pattern \d+', [re.I])
    )

    assert (
        '/pattern \d+/m' ==
        utils.convert_python_regex_to_ecma('pattern \d+', [re.M])
    )

    assert (
        '/pattern \d+/im' ==
        utils.convert_python_regex_to_ecma('pattern \d+', [re.I, re.M])
    )

    assert (
        '/ecma pattern$/' ==
        utils.convert_python_regex_to_ecma('/ecma pattern$/')
    )

    assert (
        '/ecma pattern$/im' ==
        utils.convert_python_regex_to_ecma('/ecma pattern$/im')
    )

    assert (
        '/ecma pattern$/wrong' ==
        utils.convert_python_regex_to_ecma('/ecma pattern$/wrong')
    )

    assert (
        '/ecma pattern$/m' ==
        utils.convert_python_regex_to_ecma('/ecma pattern$/m'), [re.M]
    )


def test_converters():
    assert (
        '/^ecma \d regex$/im' ==
        utils.convert_python_regex_to_ecma(
            *utils.convert_ecma_regex_to_python('/^ecma \d regex$/im'))
    )

    result = utils.convert_ecma_regex_to_python(
        utils.convert_python_regex_to_ecma(
            '^some \w python regex$', [re.I]))

    assert '^some \w python regex$' == result.regex
    assert [re.I] == result.flags
