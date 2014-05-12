"""Definitions of fields."""

import six

from .error import ValidationError


class BaseField(object):

    """Base class for all fields."""

    _types = None

    def __init__(self, required=False, data_transformer=None, help_text=None):
        """Init."""
        self.required = required
        self.data_transformer = data_transformer
        self.help_text = help_text

    @property
    def types(self):
        """Get types."""
        return self._types

    def validate(self, name, value):
        """Validate value."""
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

    def to_struct(self, value):
        """Cast value to Python structure."""
        return value

    def parse_value(self, value):
        """Parse value from primitive to desired format."""
        if self.data_transformer:
            return self.data_transformer.transform(value)
        else:
            return value

    @staticmethod
    def get_value_replacement():
        """Get replacement for field."""
        return None


class StringField(BaseField):

    """String field."""

    _types = six.string_types


class IntField(BaseField):

    """Integer field."""

    _types = (int,)


class FloatField(BaseField):

    """Float field."""

    _types = (float, int)


class ListField(BaseField):

    """List field."""

    _types = (list,)

    @property
    def items_types(self):
        """Get items types."""
        return self._items_types

    def __init__(self, items_types=None, *args, **kwargs):
        """Init."""
        if items_types:
            try:
                self._items_types = tuple(items_types)
            except TypeError:
                self._items_types = items_types,
        else:
            self._items_types = tuple()
        super(ListField, self).__init__(*args, **kwargs)

    def validate(self, name, value):
        """Validation."""
        super(ListField, self).validate(name, value)

        if len(self._items_types) == 0:
            return

        for item in value:
            if not isinstance(item, self._items_types):
                raise ValidationError(
                    'All items of "{}" must be instances '
                    'of "{}", and not "{}".'.format(
                        name,
                        ', '.join([t.__name__ for t in self._items_types]),
                        type(item).__name__
                    ))

    def to_struct(self, value):
        """Cast value to structure."""
        result = []
        for item in value:
            result.append(item.to_struct())
        return result

    @staticmethod
    def get_value_replacement():
        """Get replacement for field."""
        return list()

    def parse_value(self, values):
        """Parse value to proper type."""
        embed_type = self._items_types[0]

        if not hasattr(getattr(embed_type, 'populate', None), '__call__'):
            return values

        if len(self._items_types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self._items_types])
                )
            )

        result = self.get_value_replacement()

        try:
            for value in values:
                result.append(embed_type(**value))
        except TypeError:
            raise ValidationError('Given value for field is not iterable.')

        return result


class EmbeddedField(BaseField):

    """Field for embedded models."""

    def __init__(self, model_types, *args, **kwargs):
        """Init."""
        try:
            iter(model_types)
            self._types = tuple(model_types)
        except TypeError:
            self._types = (model_types,)

        super(EmbeddedField, self).__init__(*args, **kwargs)

    def validate(self, name, value):
        """Validation."""
        super(EmbeddedField, self).validate(name, value)
        try:
            value.validate()
        except AttributeError:
            pass

    def parse_value(self, value):
        """Parse value to proper type."""
        if len(self._types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self._types])
                )
            )
        embed_type = self._types[0]
        return embed_type(**value)
