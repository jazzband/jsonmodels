import datetime

import six
from dateutil.parser import parse

from .errors import ValidationError
from .collections import ModelCollection


class BaseField(object):

    """Base class for all fields."""

    types = None

    def __init__(
            self,
            required=False,
            help_text=None,
            validators=None):
        self._memory = {}
        self.required = required
        self.help_text = help_text
        self._assign_validators(validators)

    def _assign_validators(self, validators):
        if validators and not isinstance(validators, list):
            validators = [validators]
        self.validators = validators or []

    def __set__(self, obj, value):
        value = self.parse_value(value)
        self.validate(value)
        self._memory[obj] = value

    def __get__(self, obj, owner=None):
        if obj is None:
            return self

        self._check_value(obj)
        return self._memory[obj]

    def _check_value(self, obj):
        if obj not in self._memory:
            self.__set__(obj, self.get_default_value())

    def validate_for_object(self, obj):
        value = self.__get__(obj)
        self.validate(value)

    def validate(self, value):
        self._check_types()
        self._validate_against_types(value)
        self._check_against_required(value)
        self._validate_with_custom_validators(value)

    def _check_against_required(self, value):
        if value is None and self.required:
            raise ValidationError('Field is required!')

    def _validate_against_types(self, value):
        if value is not None and not isinstance(value, self.types):
            raise ValidationError(
                'Value is wrong, expected type "{}"'.format(
                    ', '.join([t.__name__ for t in self.types])
                ),
                value
            )

    def _check_types(self):
        if self.types is None:
            raise ValidationError(
                'Field "{}" is not usable, try '
                'different field type.'.format(type(self).__name__))

    def to_struct(self, value):
        """Cast value to Python structure."""
        return value

    def parse_value(self, value):
        """Parse value from primitive to desired format.

        Each field can parse value to form it wants it to be (like string or
        int).

        """
        return value

    def _validate_with_custom_validators(self, value):
        for validator in self.validators:
            try:
                validator.validate(value)
            except AttributeError:
                validator(value)

    @staticmethod
    def get_default_value():
        """Get default value for field.

        Each field can specify its default.

        """
        return None


class StringField(BaseField):

    """String field."""

    types = six.string_types


class IntField(BaseField):

    """Integer field."""

    types = (int,)


class FloatField(BaseField):

    """Float field."""

    types = (float, int)


class BoolField(BaseField):

    """Bool field."""

    types = (bool,)

    def parse_value(self, value):
        """Cast value to `bool`."""
        parsed = super(BoolField, self).parse_value(value)
        return bool(parsed) if parsed is not None else None


class ListField(BaseField):

    """List field."""

    types = (list,)

    def __init__(self, items_types=None, *args, **kwargs):
        """Init.

        `ListField` is **always not required**. If you want to control number
        of items use validators.

        """
        self._assign_types(items_types)
        super(ListField, self).__init__(*args, **kwargs)
        self.required = False

    def _assign_types(self, items_types):
        if items_types:
            try:
                self.items_types = tuple(items_types)
            except TypeError:
                self.items_types = items_types,
        else:
            self.items_types = tuple()

    def validate(self, value):
        super(ListField, self).validate(value)

        if len(self.items_types) == 0:
            return

        try:
            for item in value:
                self.validate_single_value(item)
        except TypeError:
            pass

    def validate_single_value(self, item):
        if len(self.items_types) == 0:
            return

        if not isinstance(item, self.items_types):
            raise ValidationError(
                'All items must be instances '
                'of "{}", and not "{}".'.format(
                    ', '.join([t.__name__ for t in self.items_types]),
                    type(item).__name__
                ))

    def to_struct(self, value):
        """Cast value to list."""
        return [item.to_struct() for item in value]

    def get_default_value(self):
        return ModelCollection(self)

    def parse_value(self, values):
        """Cast value to proper collection."""
        result = self.get_default_value()

        if not values:
            return result

        if not isinstance(values, list):
            return values

        embed_type = self.items_types[0]

        if not hasattr(getattr(embed_type, 'populate', None), '__call__'):
            return values

        self._check_items_types_count()
        self._parse_values_to_result(values, embed_type, result)

        return result

    def _check_items_types_count(self):
        if len(self.items_types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self.items_types])
                )
            )

    def _parse_values_to_result(self, values, embed_type, result):
        try:
            for value in values:
                self._append_value_to_result(value, result, embed_type)
        except TypeError:
            raise ValidationError('Given value for field is not iterable.')

    def _append_value_to_result(self, value, result, embed_type):
        if isinstance(value, self.items_types):
            result.append(value)
        else:
            result.append(embed_type(**value))


class EmbeddedField(BaseField):

    """Field for embedded models."""

    def __init__(self, model_types, *args, **kwargs):
        self._assign_model_types(model_types)
        super(EmbeddedField, self).__init__(*args, **kwargs)

    def _assign_model_types(self, model_types):
        try:
            iter(model_types)
            self.types = tuple(model_types)
        except TypeError:
            self.types = (model_types,)

    def validate(self, value):
        super(EmbeddedField, self).validate(value)
        try:
            value.validate()
        except AttributeError:
            pass

    def parse_value(self, value):
        """Parse value to proper model type."""
        if not isinstance(value, dict):
            return value

        embed_type = self._get_embed_type()
        return embed_type(**value)

    def _get_embed_type(self):
        if len(self.types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self.types])
                )
            )
        return self.types[0]


class TimeField(StringField):

    """Time field."""

    types = (datetime.time,)

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
        if isinstance(value, datetime.time):
            return value
        return parse(value).timetz()


class DateField(StringField):

    """Date field."""

    types = (datetime.date,)
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
        if isinstance(value, datetime.date):
            return value
        return parse(value).date()


class DateTimeField(StringField):

    """Datetime field."""

    types = (datetime.datetime,)

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
        if isinstance(value, datetime.datetime):
            return value
        return parse(value)
