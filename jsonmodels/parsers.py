"""Parsers to change model structure into different ones."""
import inspect

from . import fields, builders, errors


def to_struct(model):
    """Cast instance of model to python structure.

    :param model: Model to be casted.
    :rtype: ``dict``

    """
    model.validate()

    resp = {}
    for name, field in model:
        value = field.__get__(model)
        if value is None:
            continue

        value = field.to_struct(value)
        resp[name] = value
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
    builder = builders.ObjectBuilder(cls, parent_builder)
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
    builder = builders.ListBuilder(parent_builder)
    for type in field.items_types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder


def _parse_embedded(field, parent_builder):
    builder = builders.EmbeddedBuilder(parent_builder)
    for type in field.types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder


def build_json_schema_primitive(cls, parent_builder):
    builder = builders.PrimitiveBuilder(parent_builder)
    builder.set_type(cls)
    return builder


def _specify_field_type(field):
    if isinstance(field, fields.StringField):
        return {'type': 'string'}
    elif isinstance(field, fields.IntField):
        return {'type': 'number'}
    elif isinstance(field, fields.FloatField):
        return {'type': 'float'}
    elif isinstance(field, fields.BoolField):
        return {'type': 'boolean'}

    raise errors.FieldNotSupported(
        'Field {field} is not supported!'.format(
            field=type(field).__class__.__name__))
