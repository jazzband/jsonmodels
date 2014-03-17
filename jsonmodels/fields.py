
from .error import ValidationError


class BaseField(object):

    """Base class for all fields."""

    def __init__(self, required=False):
        self.required = required

    def validate(self, name, value):
        if value is None and self.required:
            raise ValidationError('Field "{}" is required!'.format(name))


class StringField(BaseField):

    """String field."""


class IntField(BaseField):

    """Integer field."""


class FloatField(BaseField):

    """Float field."""
