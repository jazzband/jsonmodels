"""Base models."""

import six

from . import parsers, errors
from .fields import BaseField


class Base(object):

    """Base class for all models."""

    def __init__(self, **kwargs):
        """Init."""
        self.populate(**kwargs)

    def populate(self, **kw):
        """Populate values to fields. Skip non-existing."""
        for name, field in self:
            if name in kw:
                field.__set__(self, kw[name])

    def get_field(self, field_name):
        """Get field associated with given attribute."""
        for attr_name, field in self:
            if field_name == attr_name:
                return field

        raise errors.FieldNotFound('Field not found', field_name)

    def __iter__(self):
        """Iterate through fields and values."""
        for name, field in self.iterate_over_fields():
            yield name, field

    @classmethod
    def iterate_over_fields(cls):
        """Iterate through fields and values."""
        for attr in dir(cls):
            clsattr = getattr(cls, attr)
            if isinstance(clsattr, BaseField):
                yield attr, clsattr

    def to_struct(self):
        """Cast model to structure."""
        return parsers.to_struct(self)

    @classmethod
    def to_json_schema(cls):
        """Cast model to JSON schema."""
        return parsers.to_json_schema(cls)

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
