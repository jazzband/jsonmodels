"""Predefined validators."""

import re
try:
    from functools import reduce
except ImportError:
    pass

from .errors import ValidationError
from . import utilities


class Min(object):

    """Validator for minimum value."""

    def __init__(self, minimum_value, exclusive=False):
        """Init.

        :param minimum_value: Minimum value for validator.
        :param bool exclusive: If `True`, then validated value must be strongly
            lower than given threshold.

        """
        self.minimum_value = minimum_value
        self.exclusive = exclusive

    def validate(self, value):
        """Validate value."""
        if self.exclusive:
            if value <= self.minimum_value:
                tpl = "'{value}' is lower or equal than minimum ('{min}')."
                raise ValidationError(
                    tpl.format(value=value, min=self.minimum_value))
        else:
            if value < self.minimum_value:
                raise ValidationError(
                    "'{value}' is lower than minimum ('{min}').".format(
                        value=value, min=self.minimum_value))

    def modify_schema(self, field_schema):
        """Modify field schema."""
        field_schema['minimum'] = self.minimum_value
        if self.exclusive:
            field_schema['exclusiveMinimum'] = True


class Max(object):

    """Validator for maximum value."""

    def __init__(self, maximum_value, exclusive=False):
        """Init.

        :param maximum_value: Maximum value for validator.
        :param bool exclusive: If `True`, then validated value must be strongly
            bigger than given threshold.

        """
        self.maximum_value = maximum_value
        self.exclusive = exclusive

    def validate(self, value):
        """Validate value."""
        if self.exclusive:
            if value >= self.maximum_value:
                tpl = "'{val}' is bigger or equal than maximum ('{max}')."
                raise ValidationError(
                    tpl.format(val=value, max=self.maximum_value))
        else:
            if value > self.maximum_value:
                raise ValidationError(
                    "'{value}' is bigger than maximum ('{max}').".format(
                        value=value, max=self.maximum_value))

    def modify_schema(self, field_schema):
        """Modify field schema."""
        field_schema['maximum'] = self.maximum_value
        if self.exclusive:
            field_schema['exclusiveMaximum'] = True


class Regex(object):

    """Validator for regular expressions."""

    FLAGS = {
        'ignorecase': re.I,
        'multiline': re.M,
    }

    def __init__(self, pattern, **flags):
        """Init.

        Note, that if given pattern is ECMA regex, given flags will be
        **completely ignored** and taken from given regex.


        :param string pattern: Pattern of regex.
        :param dict flags: Allowed flags can be found in attribute
            `ATTRIBUTES_TO_FLAGS`. Invalid flags will be ignored.

        """
        flags = dict(
            (key, value) for key, value in flags.items()
            if key in self.FLAGS
        )

        if utilities.is_ecma_regex(pattern):
            result = utilities.convert_ecma_regex_to_python(pattern)
            self.pattern = result.regex

            for key, _ in flags.items():
                flags.update(
                    {key: self.FLAGS[key] in result.flags})
        else:
            self.pattern = pattern

        self.flags = [
            self.FLAGS[key] for key, value
            in flags.items() if value]

    def validate(self, value):
        """Validate value."""
        flags = self._calculate_flags()

        try:
            result = re.search(self.pattern, value, flags)
        except TypeError as te:
            raise ValidationError(*te.args)

        if not result:
            raise ValidationError(
                'Value "{value}" did not match pattern "{pattern}".'.format(
                    value=value, pattern=self.pattern
                ))

    def _calculate_flags(self):
        return reduce(lambda x, y: x | y, self.flags, 0)

    def modify_schema(self, field_schema):
        """Modify field schema."""
        field_schema['pattern'] = utilities.convert_python_regex_to_ecma(
            self.pattern, self.flags)


class Length(object):

    """Validator for length."""

    def __init__(self, minimum_value=None, maximum_value=None):
        """Init.

        Note that if no `minimum_value` neither `maximum_value` will be
        specified, `ValueError` will be raised.

        :param int minimum_value: Minimum value (optional).
        :param int maximum_value: Maximum value (optional).

        """
        if minimum_value is None and maximum_value is None:
            raise ValueError(
                "Either 'minimum_value' or 'maximum_value' must be specified.")

        self.minimum_value = minimum_value
        self.maximum_value = maximum_value

    def validate(self, value):
        """Validate value."""
        len_ = len(value)

        if self.minimum_value is not None and len_ < self.minimum_value:
            tpl = "Value '{val}' length is lower than allowed minimum '{min}'."
            raise ValidationError(tpl.format(
                val=value, min=self.minimum_value
            ))

        if self.minimum_value is not None and len_ > self.maximum_value:
            raise ValidationError(
                "Value '{val}' length is bigger than "
                "allowed maximum '{max}'.".format(
                    val=value,
                    max=self.maximum_value,
                ))

    def modify_schema(self, field_schema):
        """Modify field schema."""
        if self.minimum_value:
            field_schema['minLength'] = self.minimum_value

        if self.maximum_value:
            field_schema['maxLength'] = self.maximum_value
