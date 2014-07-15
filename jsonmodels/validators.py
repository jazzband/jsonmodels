"""Predefined validators."""

from .error import ValidationError


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
                raise ValidationError(
                    "'{}' is lower or equal than minimum ('{}').".format(
                        value, self.minimum_value))
        else:
            if value < self.minimum_value:
                raise ValidationError(
                    "'{}' is lower than minimum ('{}').".format(
                        value, self.minimum_value))

    def modify_schema(self, field_schema):
        """Modify field schema."""
        field_schema['minimum'] = self.minimum_value
        if self.exclusive:
            field_schema['exclusiveMinimum'] = True
