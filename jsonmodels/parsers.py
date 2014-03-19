"""Parsers to change model structure into different one."""


def to_struct(model):
    """Cast model to python structure.

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

        if isinstance(value, list):
            resp[name] = [to_struct(item) for item in value]
        else:
            resp[name] = to_struct(value)
    return resp
