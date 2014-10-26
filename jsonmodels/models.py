import six

from . import parsers, errors
from .fields import BaseField


class Base(object):

    """Base class for all models."""

    def __init__(self, **kwargs):
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

    def validate(self):
        """Explicitly validate all the fields."""
        for _, field in self:
            field.validate_for_object(self)

    @classmethod
    def iterate_over_fields(cls):
        """Iterate through fields and values."""
        for attr in dir(cls):
            clsattr = getattr(cls, attr)
            if isinstance(clsattr, BaseField):
                yield attr, clsattr

    def to_struct(self):
        """Cast model to Python structure."""
        return parsers.to_struct(self)

    @classmethod
    def to_json_schema(cls):
        """Generate JSON schema for model."""
        return parsers.to_json_schema(cls)

    def __repr__(self):
        try:
            txt = six.text_type(self)
        except TypeError:
            txt = ''
        return '<{}: {}>'.format(self.__class__.__name__, txt)

    def __str__(self):
        return '{} object'.format(self.__class__.__name__)
