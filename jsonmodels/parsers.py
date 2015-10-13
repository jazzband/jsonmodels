"""Parsers to change model structure into different ones."""
import inspect

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


def to_json_schema(cls, counter=None):
    """Generate JSON schema for given class.

    :param cls: Class to be casted.
    :param counter: Builder like object to keep state between recursive calls.
    :rtype: ``dict``

    """
    builder = build_json_schema(cls)
    return builder.build()


def build_json_schema(value):
    from .models import Base

    cls = value if inspect.isclass(value) else value.__class__
    if issubclass(cls, Base):
        return build_json_schema_object(cls)
    else:
        return build_json_schema_primitive(cls)


def build_json_schema_object(cls):
    builder = ObjectBuilder()
    for name, field in cls.iterate_over_fields():
        if isinstance(field, fields.EmbeddedField):
            builder.add_field(name, field, _parse_embedded(field))
        elif isinstance(field, fields.ListField):
            builder.add_field(name, field, _parse_list(field))
        else:
            builder.add_field(name, field, _specify_field_type(field))
    return builder


def build_json_schema_primitive(cls):
    builder = PrimitiveBuilder()
    builder.set_type(cls)
    return builder


class Builder(object):

    def __init__(self):
        self.parent = None

    @classmethod
    def maybe_build(cls, value):
        return value.build() if isinstance(value, Builder) else value


class ObjectBuilder(Builder):

    def __init__(self):
        super(ObjectBuilder, self).__init__()
        self.properties = {}
        self.required = []

    def add_field(self, name, field, schema):
        _apply_validators_modifications(schema, field)
        self.properties[name] = schema
        if field.required:
            self.required.append(name)

    def build(self):
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
        return schema


class PrimitiveBuilder(Builder):

    def __init__(self):
        super(PrimitiveBuilder, self).__init__()
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


def _parse_list(field):
    builder = ListBuilder()
    for type in field.items_types:
        builder.add_type_schema(build_json_schema(type))
    return builder


class ListBuilder(Builder):

    def __init__(self):
        super(ListBuilder, self).__init__()
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


def _specify_field_type(field):
    if isinstance(field, fields.StringField):
        return {'type': 'string'}
    elif isinstance(field, fields.IntField):
        return {'type': 'integer'}
    elif isinstance(field, fields.FloatField):
        return {'type': 'float'}
    elif isinstance(field, fields.BoolField):
        return {'type': 'boolean'}


def _parse_embedded(field):
    builder = EmbeddedBuilder()
    for type in field.types:
        builder.add_type_schema(build_json_schema(type))
    return builder


class EmbeddedBuilder(Builder):

    def __init__(self):
        super(EmbeddedBuilder, self).__init__()
        self.schemas = []

    def add_type_schema(self, schema):
        self.schemas.append(schema)

    def build(self):
        schemas = [self.maybe_build(schema) for schema in self.schemas]
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {'oneOf': schemas}
