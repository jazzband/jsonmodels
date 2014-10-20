"""Definitions of fields."""

import datetime

import six
from dateutil.parser import parse

from .errors import ValidationError


class BaseField(object):

    """Base class for all fields."""

    types = None

    def __init__(
            self,
            required=False,
            help_text=None,
            validators=None):
        """Init."""
        self._memory = {}
        self.required = required
        self.help_text = help_text

        if validators and not isinstance(validators, list):
            validators = [validators]
        self.validators = validators or []

    def __set__(self, obj, value):
        """Set value."""
        value = self.parse_value(value)
        name = self._get_name_for(obj)
        self.validate(value, name)
        self._memory[obj] = value

    def __get__(self, obj, owner=None):
        """Get value."""
        if obj is None:
            return self

        self._check_value(obj)
        return self._memory[obj]

    def _check_value(self, obj):
        if obj not in self._memory:
            self.__set__(obj, self.get_default_value())

    def validate_for(self, obj):
        """Validate given object."""
        value = self.__get__(obj)
        name = self._get_name_for(obj)
        self.validate(value, name)

    def _get_name_for(self, obj):
        for name, field in obj:
            if field is field:
                return name

        raise ValueError('Name for object not found!', field, obj)

    def validate(self, value, name):
        """Validate value."""
        if self.types is None:
            raise ValidationError(
                'Field "{}" is of type "{}" that is not usable, try '
                'different field type.'.format(name, type(self).__name__))

        if value is not None and not isinstance(value, self.types):
            raise ValidationError(
                'Value of field "{}" is wrong, expected type "{}"'.format(
                    name,
                    ', '.join([t.__name__ for t in self.types])
                ))

        if value is None and self.required:
            raise ValidationError('Field "{}" is required!'.format(name))

        self._validate_with_custom_validators(value)

    def to_struct(self, value):
        """Cast value to Python structure."""
        return value

    def parse_value(self, value):
        """Parse value from primitive to desired format."""
        return value

    def _validate_with_custom_validators(self, value):
        if self.validators:
            for validator in self.validators:
                try:
                    validator.validate(value)
                except AttributeError:
                    validator(value)

    @staticmethod
    def get_default_value():
        """Get replacement for field."""
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
        if items_types:
            try:
                self.items_types = tuple(items_types)
            except TypeError:
                self.items_types = items_types,
        else:
            self.items_types = tuple()
        super(ListField, self).__init__(*args, **kwargs)
        self.required = False

    def validate(self, value, name):
        """Validation."""
        super(ListField, self).validate(value, name)

        if len(self.items_types) == 0:
            return

        try:
            for item in value:
                self.validate_single_item(item, name)
        except TypeError:
            pass

    def validate_single_item(self, item, name):
        if not isinstance(item, self.items_types):
            raise ValidationError(
                'All items of "{}" must be instances '
                'of "{}", and not "{}".'.format(
                    name,
                    ', '.join([t.__name__ for t in self.items_types]),
                    type(item).__name__
                ))

    def to_struct(self, value):
        """Cast value to structure."""
        result = []
        for item in value:
            result.append(item.to_struct())
        return result

    @staticmethod
    def get_default_value():
        """Get replacement for field."""
        return list()

    def parse_value(self, values):
        """Parse value to proper type."""
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
                if isinstance(value, self.items_types):
                    result.append(value)
                else:
                    result.append(embed_type(**value))
        except TypeError:
            raise ValidationError('Given value for field is not iterable.')


class EmbeddedField(BaseField):

    """Field for embedded models."""

    def __init__(self, model_types, *args, **kwargs):
        """Init."""
        try:
            iter(model_types)
            self.types = tuple(model_types)
        except TypeError:
            self.types = (model_types,)

        super(EmbeddedField, self).__init__(*args, **kwargs)

    def validate(self, value, name):
        """Validation."""
        super(EmbeddedField, self).validate(value, name)
        try:
            value.validate()
        except AttributeError:
            pass

    def parse_value(self, value):
        """Parse value to proper type."""
        if not isinstance(value, dict):
            return value

        if len(self.types) != 1:
            raise ValidationError(
                'Cannot decide which type to choose from "{}".'.format(
                    ', '.join([t.__name__ for t in self.types])
                )
            )
        embed_type = self.types[0]

        return embed_type(**value)


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
