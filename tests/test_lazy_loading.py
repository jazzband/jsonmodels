import pytest

from jsonmodels import models, fields, errors


class Primary(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('Secondary')


class Third(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('tests.test_lazy_loading.Secondary')


class Fourth(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('.Secondary')


class Fifth(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('..test_lazy_loading.Secondary')


class Sixth(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('...tests.test_lazy_loading.Secondary')


class Seventh(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('....tests.test_lazy_loading.Secondary')


class Eighth(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('.SomeWrongEntity')


class Secondary(models.Base):

    data = fields.IntField()


@pytest.mark.parametrize(['model'], [
    (Primary,),
    (Third,),
    (Fourth,),
    (Fifth,),
    (Sixth,),
])
def test_embedded_model(model):
    entity = model()
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


def test_relative_too_much():
    with pytest.raises(ValueError):
        Seventh()


def test_wrong_entity():
    with pytest.raises(ValueError):
        Eighth()
