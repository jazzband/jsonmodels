"""Parsers to change model structure into different ones."""
from __future__ import absolute_import

import inspect
from collections import defaultdict

import six

from . import fields


def to_struct(model):
    """Cast instance of model to python structure.

    :param model: Model to be casted.
    :rtype: ``dict``

    """
    from .models import Base

    if not isinstance(model, Base):
        return model

    model.validate()

    resp = {}
    for name, field in model:
        value = field.__get__(model)
        if value is None:
            continue

        if isinstance(value, list):
            resp[name] = [to_struct(item) for item in value]
        else:
            resp[name] = to_struct(value)
    return resp


def to_json_schema(cls):
    """Generate JSON schema for given class.

    :param cls: Class to be casted.
    :rtype: ``dict``

    """
    builder = build_json_schema(cls)
    return builder.build()


def build_json_schema(value, parent_builder=None):
    from .models import Base

    cls = value if inspect.isclass(value) else value.__class__
    if issubclass(cls, Base):
        return build_json_schema_object(cls, parent_builder)
    else:
        return build_json_schema_primitive(cls, parent_builder)


def build_json_schema_object(cls, parent_builder=None):
    builder = ObjectBuilder(cls, parent_builder)
    if builder.count_type(builder.type) > 1:
        return builder
    for name, field in cls.iterate_over_fields():
        if isinstance(field, fields.EmbeddedField):
            builder.add_field(name, field, _parse_embedded(field, builder))
        elif isinstance(field, fields.ListField):
            builder.add_field(name, field, _parse_list(field, builder))
        else:
            builder.add_field(name, field, _specify_field_type(field))
    return builder


def _parse_list(field, parent_builder):
    builder = ListBuilder(parent_builder)
    for type in field.items_types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder


def _parse_embedded(field, parent_builder):
    builder = EmbeddedBuilder(parent_builder)
    for type in field.types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder


def build_json_schema_primitive(cls, parent_builder):
    builder = PrimitiveBuilder(parent_builder)
    builder.set_type(cls)
    return builder


class Builder(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.types_builders = {}
        self.types_count = defaultdict(int)
        self.definitions = set()

    def register_type(self, type, builder):
        if self.parent:
            return self.parent.register_type(type, builder)

        self.types_count[type] += 1
        if type not in self.types_builders:
            self.types_builders[type] = builder

    def get_builder(self, type):
        if self.parent:
            return self.parent.get_builder(type)

        return self.types_builders[type]

    def count_type(self, type):
        if self.parent:
            return self.parent.count_type(type)

        return self.types_count[type]

    @staticmethod
    def maybe_build(value):
        return value.build() if isinstance(value, Builder) else value

    def add_definition(self, builder):
        if self.parent:
            return self.parent.add_definition(builder)

        self.definitions.add(builder)


class ObjectBuilder(Builder):

    def __init__(self, model_type, *args, **kwargs):
        super(ObjectBuilder, self).__init__(*args, **kwargs)
        self.properties = {}
        self.required = []
        self.type = model_type

        self.register_type(self.type, self)

    def add_field(self, name, field, schema):
        _apply_validators_modifications(schema, field)
        self.properties[name] = schema
        if field.required:
            self.required.append(name)

    def build(self):
        if self.is_definition and not self.is_root:
            builder = self.get_builder(self.type)
            self.add_definition(builder)
            [self.maybe_build(value) for _, value in self.properties.items()]
            return '#/definitions/{}'.format(self.type_name)
        else:
            builder = self.get_builder(self.type)
            return builder.build_definition()

    @property
    def type_name(self):
        module_name = '{}.{}'.format(self.type.__module__, self.type.__name__)
        return module_name.replace('.', '_').lower()

    def build_definition(self, add_defintitions=True):
        properties = {
            name: self.maybe_build(value)
            for name, value
            in self.properties.items()
        }
        schema = {
            'type': 'object',
            'additionalProperties': False,
            'properties': properties,
        }
        if self.required:
            schema['required'] = self.required
        if self.definitions and add_defintitions:
            schema['definitions'] = {
                builder.type_name: builder.build_definition(False)
                for builder in self.definitions
            }
        return schema

    @property
    def is_definition(self):
        if self.count_type(self.type) > 1:
            return True
        elif self.parent:
            return self.parent.is_definition
        else:
            return False

    @property
    def is_root(self):
        return not bool(self.parent)


class PrimitiveBuilder(Builder):

    def __init__(self, *args, **kwargs):
        super(PrimitiveBuilder, self).__init__(*args, **kwargs)
        self.type = None

    def set_type(self, type):
        self.type = type

    def build(self):
        if issubclass(self.type, six.string_types):
            return {'type': 'string'}
        elif issubclass(self.type, int):
            return {'type': 'integer'}
        elif issubclass(self.type, float):
            return {'type': 'float'}
        elif issubclass(self.type, bool):
            return {'type': 'boolean'}

        raise ValueError("Can't specify value schema!", self.type)


def _apply_validators_modifications(field_schema, field):
    for validator in field.validators:
        try:
            validator.modify_schema(field_schema)
        except AttributeError:
            pass


class ListBuilder(Builder):

    def __init__(self, *args, **kwargs):
        super(ListBuilder, self).__init__(*args, **kwargs)
        self.schemas = []

    def add_type_schema(self, schema):
        self.schemas.append(schema)

    def build(self):
        result = {'type': 'list'}

        schemas = [self.maybe_build(schema) for schema in self.schemas]
        if len(schemas) == 1:
            items = schemas[0]
        elif len(schemas) > 1:
            items = {'oneOf': schemas}

        if items:
            result['items'] = items
        return result

    @property
    def is_definition(self):
        return self.parent.is_definition


def _specify_field_type(field):
    if isinstance(field, fields.StringField):
        return {'type': 'string'}
    elif isinstance(field, fields.IntField):
        return {'type': 'integer'}
    elif isinstance(field, fields.FloatField):
        return {'type': 'float'}
    elif isinstance(field, fields.BoolField):
        return {'type': 'boolean'}


class EmbeddedBuilder(Builder):

    def __init__(self, *args, **kwargs):
        super(EmbeddedBuilder, self).__init__(*args, **kwargs)
        self.schemas = []

    def add_type_schema(self, schema):
        self.schemas.append(schema)

    def build(self):
        schemas = [self.maybe_build(schema) for schema in self.schemas]
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {'oneOf': schemas}

    @property
    def is_definition(self):
        return self.parent.is_definition
