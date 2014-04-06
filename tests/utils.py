"""Utilities for tests."""

import os
import json

import six

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'fixtures'
)

# Scalar types are types allowed in schemes besides dicts and lists.
SCALAR_TYPES = tuple(list(six.string_types) + [int, float, bool])


def get_fixture(filepath):
    """Get fixture content.

    :param string filepath: Path to file.

    """
    with open(os.path.join(FIXTURES_DIR, filepath)) as fixture:
        return json.loads(fixture.read())

def _normalize_string_type(value):
    if isinstance(value, six.string_types):
        return six.text_type(value)
    else:
        return value


def _compare_dicts(one, two):
    for key, value in one.items():
        if not compare_schemes(one[key], two[key]):
            return False
    return True


def _compare_lists(one, two):
    for first_item in one:
        result = False
        for second_item in two:
            # Skipping loop if previously found match.
            if not result:
                result = compare_schemes(first_item, second_item)
        if not result:
            return False
    return True


def compare_schemes(one, two):
    """Compare two structures that represents JSON schemes.

    For comprison you can't use normal comparison, because in JSON scheme lists
    DO NOT keep order (and Python lists do), so this must be taken into account
    during compaison.

    Note this wont check all configurations, only first one that seems to
    match, which can lead to wrong results.

    :param one: First sheme to compare.
    :param two: Second scheme to compare.
    :rtype: `bool`

    """
    # Casting string and unicode types to one type.
    one = _normalize_string_type(one)
    two = _normalize_string_type(two)

    if not isinstance(one, type(two)) or not isinstance(two, type(one)):
        raise RuntimeError('Types mismatch! "{}" and "{}".'.format(
            type(one).__name__, type(two).__name__))

    # From now on we can assume both argument have the same type.
    if isinstance(one, list):
        return _compare_lists(one, two)
    elif isinstance(one, dict):
        return _compare_dicts(one, two)
    elif isinstance(one, SCALAR_TYPES):
        return one == two
    else:
        raise RuntimeError('Not allowed type "{}"'.format(type(one).__name__))
