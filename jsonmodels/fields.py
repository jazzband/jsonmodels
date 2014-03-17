
from .error import ValidationError


class BaseField(object):

    """Base class for all fields."""

    _types = None

    def __init__(self, required=False):
        self.required = required

    def validate(self, name, value):
        if self._types is None:
            raise ValidationError(
                'Field "{}" is of type "{}" that is not usable, try '
                'different field type.'.format(name, type(self).__name__))

        if value is not None and not isinstance(value, self._types):
            raise ValidationError(
                'Value of field "{}" is wrong, expected {}'.format(
                    name,
                    ', '.join([t.__name__ for t in self._types])
                ))

        if value is None and self.required:
            raise ValidationError('Field "{}" is required!'.format(name))


class StringField(BaseField):

    """String field."""

    _types = (str, basestring, unicode)


class IntField(BaseField):

    """Integer field."""

    _types = (int,)


class FloatField(BaseField):

    """Float field."""

    _types = (float, int)
