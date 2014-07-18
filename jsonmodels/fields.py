"""Definitions of fields."""

import datetime

import six
from dateutil.parser import parse

from .error import ValidationError


class BaseField(object):

    """Base class for all fields."""

    _types = None

    def __init__(
            self,
            required=False,
            data_transformer=None,
            help_text=None,
            validators=None):
        """Init."""
        self.required = required
        self.data_transformer = data_transformer
        self.help_text = help_text

        if validators and not isinstance(validators, list):
            validators = [validators]
        self.validators = validators or []

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
                'Value of field "{}" is wrong, expected type "{}"'.format(
                    name,
                    ', '.join([t.__name__ for t in self._types])
                ))

        if value is None and self.required:
            raise ValidationError('Field "{}" is required!'.format(name))

        self._validate_with_custom_validators(value)

    def to_struct(self, value):
        """Cast value to Python structure."""
        return value

    def parse_value(self, value):
        """Parse value from primitive to desired format."""
        if self.data_transformer:
            return self.data_transformer.transform(value)
        else:
            return value

    def _validate_with_custom_validators(self, value):
        if self.validators:
            for validator in self.validators:
                try:
                    validator.validate(value)
                except AttributeError:
                    validator(value)

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


class BoolField(BaseField):

    """Bool field."""

    _types = (bool,)

    def parse_value(self, value):
        """Cast value to `bool`."""
        parsed = super(BoolField, self).parse_value(value)
        return bool(parsed) if parsed is not None else None


class ListField(BaseField):

    """List field."""

    _types = (list,)

    @property
    def items_types(self):
        """Get items types."""
        return self._items_types

    def __init__(self, items_types=None, *args, **kwargs):
        """Init.

        `ListField` is **always not required**. If you want to control number
        of items use validators.

        """
        if items_types:
            try:
                self._items_types = tuple(items_types)
            except TypeError:
                self._items_types = items_types,
        else:
            self._items_types = tuple()
        super(ListField, self).__init__(*args, **kwargs)
        self.required = False

    def validate(self, name, value):
        """Validation."""
        super(ListField, self).validate(name, value)

        if len(self._items_types) == 0:
            return

        try:
            for item in value:
                if not isinstance(item, self._items_types):
                    raise ValidationError(
                        'All items of "{}" must be instances '
                        'of "{}", and not "{}".'.format(
                            name,
                            ', '.join([t.__name__ for t in self._items_types]),
                            type(item).__name__
                        ))
        except TypeError:
            pass

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
        if not isinstance(value, dict):
            return value

        if len(self._types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self._types])
                )
            )
        embed_type = self._types[0]

        return embed_type(**value)


class TimeField(StringField):

    """Time field."""

    _types = (datetime.time,)

    def __init__(self, str_format=None, *args, **kwargs):
        """Init.

        :param str str_format: Format to cast time to (if `None` - casting to
            ISO 8601 format).

        """
        self.str_format = str_format
        super(TimeField, self).__init__(*args, **kwargs)

    def to_struct(self, value):
        """Cast `time` object to string."""
        if self.str_format:
            return value.strftime(self.str_format)
        return value.isoformat()

    def parse_value(self, value):
        """Parse string into instance of `time`."""
        return parse(value).timetz()


class DateField(StringField):

    """Date field."""

    _types = (datetime.date,)
    default_format = '%Y-%m-%d'

    def __init__(self, str_format=None, *args, **kwargs):
        """Init.

        :param str str_format: Format to cast date to (if `None` - casting to
            %Y-%m-%d format).

        """
        self.str_format = str_format
        super(DateField, self).__init__(*args, **kwargs)

    def to_struct(self, value):
        """Cast `date` object to string."""
        if self.str_format:
            return value.strftime(self.str_format)
        return value.strftime(self.default_format)

    def parse_value(self, value):
        """Parse string into instance of `date`."""
        return parse(value).date()


class DateTimeField(StringField):

    """Datetime field."""

    _types = (datetime.datetime,)

    def __init__(self, str_format=None, *args, **kwargs):
        """Init.

        :param str str_format: Format to cast datetime to (if `None` - casting
            to ISO 8601 format).

        """
        self.str_format = str_format
        super(DateTimeField, self).__init__(*args, **kwargs)

    def to_struct(self, value):
        """Cast `datetime` object to string."""
        if self.str_format:
            return value.strftime(self.str_format)
        return value.isoformat()

    def parse_value(self, value):
        """Parse string into instance of `datetime`."""
        return parse(value)
