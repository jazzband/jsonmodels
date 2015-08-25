import pytest

from jsonmodels import models, fields, errors


class Primary(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('Secondary')


class Secondary(models.Base):

    data = fields.IntField()


def test_embedded_model():

    entity = Primary()
    assert entity.secondary is None
    entity.name = 'chuck'
    entity.secondary = Secondary()
    entity.secondary.data = 42

    with pytest.raises(errors.ValidationError):
        entity.secondary.data = '42'

    entity.secondary.data = 42

    with pytest.raises(errors.ValidationError):
        entity.secondary = 'something different'

    entity.secondary = None
