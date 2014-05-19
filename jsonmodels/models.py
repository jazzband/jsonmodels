"""Base models."""

import six

from . import parsers
from .fields import BaseField


class BaseMetaclass(type):

    """Metaclass for models."""

    def __new__(cls, class_name, bases, attr):
        """Rewriting defined fields."""
        fields = {}
        for name, field in attr.items():
            if isinstance(field, BaseField):
                attr[name] = field.get_value_replacement()
                fields[name] = field
        attr['_fields'] = fields

        return super(BaseMetaclass, cls).__new__(cls, class_name, bases, attr)


class PreBase(object):

    """Base class for all models.

    For compatibility reasons (Python 2 and 3) it is called `PreBase` and
    models MUST in fact inherit from class `Base`, otherwise it won't work.

    """

    def __init__(self, **kwargs):
        """Init."""
        self.populate(**kwargs)

    def populate(self, **kw):
        """Populate values to fields. Skip non-existing."""
        for name, value in kw.items():
            try:
                field = self._fields[name]
            except KeyError:
                continue

            parsed_value = field.parse_value(value)

            setattr(self, name, parsed_value)

    def get_field(self, name):
        """Get field associated with given attribute."""
        return self._fields[name]

    def validate(self):
        """Validate."""
        for name, field in self._fields.items():
            value = getattr(self, name)
            field.validate(name, value)

    def __iter__(self):
        """Iterate through fields and values."""
        for name, field in self._fields.items():
            value = getattr(self, name)
            yield name, value

    def to_struct(self):
        """Cast model to structure."""
        return parsers.to_struct(self)

    def to_json_schema(self):
        """Cast model to JSON schema."""
        return parsers.to_json_schema(self)

    def __repr__(self):
        """Get representation of model."""
        try:
            txt = six.text_type(self)
        except TypeError:
            txt = ''
        return '<{}: {}>'.format(self.__class__.__name__, txt)

    def __str__(self):
        """Get informal representation."""
        return '{} object'.format(self.__class__.__name__)

# Actual base for models.
Base = BaseMetaclass('Base', (PreBase,), {})
