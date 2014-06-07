"""Utilities."""

import six

SCALAR_TYPES = tuple(list(six.string_types) + [int, float, bool])


def _normalize_string_type(value):
    if isinstance(value, six.string_types):
        return six.text_type(value)
    else:
        return value


def _compare_dicts(one, two):
    if len(one) != len(two):
        return False

    for key, value in one.items():
        if key not in one or key not in two:
            return False

        if not compare_schemas(one[key], two[key]):
            return False
    return True


def _compare_lists(one, two):
    if len(one) != len(two):
        return False

    for first_item in one:
        result = False
        for second_item in two:
            if result:
                continue
            result = compare_schemas(first_item, second_item)
        if not result:
            return False
    return True


def _assert_same_types(one, two):
    if not isinstance(one, type(two)) or not isinstance(two, type(one)):
        raise RuntimeError('Types mismatch! "{}" and "{}".'.format(
            type(one).__name__, type(two).__name__))


def compare_schemas(one, two):
    """Compare two structures that represents JSON schemas.

    For comparison you can't use normal comparison, because in JSON schema
    lists DO NOT keep order (and Python lists do), so this must be taken into
    account during comparison.

    Note this wont check all configurations, only first one that seems to
    match, which can lead to wrong results.

    :param one: First schema to compare.
    :param two: Second schema to compare.
    :rtype: `bool`

    """
    one = _normalize_string_type(one)
    two = _normalize_string_type(two)

    _assert_same_types(one, two)

    if isinstance(one, list):
        return _compare_lists(one, two)
    elif isinstance(one, dict):
        return _compare_dicts(one, two)
    elif isinstance(one, SCALAR_TYPES):
        return one == two
    else:
        raise RuntimeError('Not allowed type "{}"'.format(type(one).__name__))
