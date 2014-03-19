"""Base models."""

from .fields import BaseField


class BaseMetaclass(type):

    """Metaclass for models."""

    def __new__(cls, name, bases, attr):

        fields = {}
        for name, field in attr.items():
            if isinstance(field, BaseField):
                attr[name] = field.get_value_replacement()
                fields[name] = field
        attr['_fields'] = fields

        return super(BaseMetaclass, cls).__new__(cls, name, bases, attr)


class Base(object):

    """Base class for all models."""

    __metaclass__ = BaseMetaclass

    def __init__(self, **kw):
        to_assign = {k: v for k, v in kw.items() if k in self._fields.keys()}
        for name, value in to_assign.items():
            setattr(self, name, value)

    def get_field(self, name):
        return self._fields[name]

    def validate(self):
        for name, field in self._fields.items():
            value = getattr(self, name)
            field.validate(name, value)

    def to_struct(self):
        self.validate()
        result = {}

        for name, field in self._fields.items():
            value = getattr(self, name)
            if value is not None:
                if isinstance(value, Base):
                    result[name] = value.to_struct()
                elif isinstance(field, BaseField):
                    result[name] = field.to_struct(value)

        return result

    def __iter__(self):
        for name, field in self._fields.items():
            value = getattr(self, name)
            yield name, value
