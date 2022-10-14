"""Parsers to change model structure into different ones."""
import inspect
from typing import Any

from . import builders, errors, fields


def to_struct(model: fields.Model) -> dict[str, Any]:
    """Cast instance of model to python structure."""
    model.validate()

    resp = {}
    for _, name, field in model.iterate_with_name():
        value = field.__get__(model)
        if value is None:
            continue

        value = field.to_struct(value)
        resp[name] = value
    return resp


def to_json_schema(cls: fields.Model) -> dict[str, Any]:
    """Generate JSON schema for given class."""
    builder = build_json_schema(cls)
    return builder.build()


def build_json_schema(
    value, parent_builder=None
) -> builders.PrimitiveBuilder | builders.ObjectBuilder:
    from .models import Base

    cls = value if inspect.isclass(value) else value.__class__
    if issubclass(cls, Base):
        return build_json_schema_object(cls, parent_builder)
    else:
        return build_json_schema_primitive(cls, parent_builder)


def build_json_schema_object(cls, parent_builder=None) -> builders.ObjectBuilder:
    builder = builders.ObjectBuilder(cls, parent_builder)
    if builder.count_type(builder.type) > 1:
        return builder
    for _, name, field in cls.iterate_with_name():
        if isinstance(field, fields.EmbeddedField):
            builder.add_field(name, field, _parse_embedded(field, builder))
        elif isinstance(field, fields.ListField):
            builder.add_field(name, field, _parse_list(field, builder))
        else:
            builder.add_field(name, field, _create_primitive_field_schema(field))
    return builder


def _parse_list(field, parent_builder) -> dict[str, Any]:
    builder = builders.ListBuilder(
        parent_builder, field.nullable, default=field._default
    )
    for type in field.items_types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder.build()


def _parse_embedded(field, parent_builder) -> dict[str, Any] | fields.Value:
    builder = builders.EmbeddedBuilder(
        parent_builder, field.nullable, default=field._default
    )
    for type in field.types:
        builder.add_type_schema(build_json_schema(type, builder))
    return builder.build()


def build_json_schema_primitive(cls, parent_builder) -> builders.PrimitiveBuilder:
    builder = builders.PrimitiveBuilder(cls, parent_builder)
    return builder


def _create_primitive_field_schema(field) -> dict[str, Any]:
    if isinstance(field, fields.StringField):  # TODO rewrite this as switch case?
        obj_type = "string"
    elif isinstance(field, fields.IntField):
        obj_type = "number"
    elif isinstance(field, fields.FloatField):
        obj_type = "float"
    elif isinstance(field, fields.BoolField):
        obj_type = "boolean"
    elif isinstance(field, fields.DictField):
        obj_type = "object"
    else:
        raise errors.FieldNotSupported(
            f"Field {type(field).__class__.__name__} is not supported!"
        )

    schema: dict[str, Any] = {}
    if field.nullable:
        schema = {"type": [obj_type, "null"]}
    else:
        schema = {"type": obj_type}

    if field.has_default:
        schema["default"] = field._default

    return schema
