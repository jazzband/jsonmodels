
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

    @staticmethod
    def get_value_replacement():
        """Get replacement for field."""
        return None


class StringField(BaseField):

    """String field."""

    _types = (str, basestring, unicode)


class IntField(BaseField):

    """Integer field."""

    _types = (int,)


class FloatField(BaseField):

    """Float field."""

    _types = (float, int)


class ListField(BaseField):

    """List field."""

    _types = (list,)

    def __init__(self, items_types=None, *args, **kwargs):
        self._items_types=items_types
        super(ListField, self).__init__(*args, **kwargs)

    @staticmethod
    def get_value_replacement():
        """Get replacement for field."""
        return list()
