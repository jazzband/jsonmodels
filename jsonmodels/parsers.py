"""Parsers to change model structure into different one."""

from . import fields


def to_struct(model):
    """Cast instance of model to python structure.

    :param model: Model to be casted.
    :rtype: ``dict``

    """
    try:
        model.validate()
    except AttributeError:
        return model

    resp = {}
    for name, value in model:
        if value is None:
            continue

        field = model.get_field(name)

        if hasattr(field.data_transformer, 'reverse_transform'):
            value = field.data_transformer.reverse_transform(value)

        if isinstance(value, list):
            resp[name] = [to_struct(item) for item in value]
        else:
            resp[name] = to_struct(value)
    return resp


def _specify_field_type(field):
    if isinstance(field, fields.StringField):
        return {'type': 'string'}
    elif isinstance(field, fields.IntField):
        return {'type': 'integer'}
    elif isinstance(field, fields.FloatField):
        return {'type': 'float'}


def _parse_embedded(field):
    types = field.types
    if len(types) == 1:
        instance = types[0]()
        return instance.to_json_schema()
    else:
        return {'oneOf': [ins().to_json_schema() for ins in types]}


def _parse_list(field):
    types = field.items_types
    types_len = len(types)

    if types_len == 0:
        items = None
    if types_len == 1:
        instance = types[0]()
        items = instance.to_json_schema()
    elif types_len > 1:
        items = {
            'oneOf': [ins().to_json_schema() for ins in types]}

    result = {'type': 'list'}
    if items:
        result['items'] = items

    return result


def to_json_schema(model):
    """Generate JSON schema for given instance of model.

    :param model: Model to be casted.
    :rtype: ``dict``

    """
    resp = {
        'type': 'object',
        'additionalProperties': False,
    }

    prop = {}
    required = []
    for name, _ in model:
        field = model.get_field(name)

        if field.required:
            required.append(name)

        if isinstance(field, fields.EmbeddedField):
            prop[name] = _parse_embedded(field)
        elif isinstance(field, fields.ListField):
            prop[name] = _parse_list(field)
        else:
            prop[name] = _specify_field_type(field)

    resp['properties'] = prop
    if required:
        resp['required'] = required

    return resp
