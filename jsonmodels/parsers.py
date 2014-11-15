"""Parsers to change model structure into different ones."""

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
    resp = {
        'type': 'object',
        'additionalProperties': False,
    }

    prop = {}
    required = []

    for name, field in cls.iterate_over_fields():

        if field.required:
            required.append(name)

        if isinstance(field, fields.EmbeddedField):
            prop[name] = _parse_embedded(field)
        elif isinstance(field, fields.ListField):
            prop[name] = _parse_list(field)
        else:
            prop[name] = _specify_field_type(field)

        _apply_validators_modifications(prop[name], field)

    resp['properties'] = prop
    if required:
        resp['required'] = required

    return resp


def _apply_validators_modifications(field_schema, field):
    for validator in field.validators:
        try:
            validator.modify_schema(field_schema)
        except AttributeError:
            pass


def _parse_list(field):
    types = field.items_types
    types_len = len(types)

    if types_len == 0:
        items = None
    if types_len == 1:
        cls = types[0]
        items = _parse_item(cls)
    elif types_len > 1:
        items = {
            'oneOf': [_parse_item(item) for item in types]}

    result = {'type': 'list'}
    if items:
        result['items'] = items

    return result


def _parse_item(item):
    from .models import Base

    if issubclass(item, Base):
        return item.to_json_schema()
    else:
        return _specify_field_type_for_primitive(item)


def _specify_field_type(field):
    if isinstance(field, fields.StringField):
        return {'type': 'string'}
    elif isinstance(field, fields.IntField):
        return {'type': 'integer'}
    elif isinstance(field, fields.FloatField):
        return {'type': 'float'}
    elif isinstance(field, fields.BoolField):
        return {'type': 'boolean'}


def _specify_field_type_for_primitive(value):
    if issubclass(value, six.string_types):
        return {'type': 'string'}
    elif issubclass(value, int):
        return {'type': 'integer'}
    elif issubclass(value, float):
        return {'type': 'float'}
    elif issubclass(value, bool):
        return {'type': 'boolean'}


def _parse_embedded(field):
    types = field.types
    if len(types) == 1:
        cls = types[0]
        return cls.to_json_schema()
    else:
        return {'oneOf': [cls.to_json_schema() for cls in types]}
