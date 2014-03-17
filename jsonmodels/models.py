#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def validate(self):
        for name, field in self._fields.items():
            value = getattr(self, name)
            field.validate(name, value)
