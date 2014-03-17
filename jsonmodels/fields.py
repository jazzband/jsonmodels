"""Definitions of fields."""

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
        self._items_types = tuple(items_types) if items_types else tuple()
        super(ListField, self).__init__(*args, **kwargs)

    def validate(self, name, value):
        """Validation."""
        super(ListField, self).validate(name, value)

        if len(self._items_types) == 0:
            return

        for item in value:
            if not isinstance(item, self._items_types):
                raise ValidationError(
                    'All items of "{}" must be instances of {}'.format(
                        name,
                        ', '.join([t.__name__ for t in self._items_types])
                    ))

    @staticmethod
    def get_value_replacement():
        """Get replacement for field."""
        return list()
