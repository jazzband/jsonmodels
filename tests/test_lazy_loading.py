import pytest

from jsonmodels import errors, fields, models


class Primary(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("Secondary")


class Third(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("tests.test_lazy_loading.Secondary")


class Fourth(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField(".Secondary")


class Fifth(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("..test_lazy_loading.Secondary")


class Sixth(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("...tests.test_lazy_loading.Secondary")


class Seventh(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("....tests.test_lazy_loading.Secondary")


class Eighth(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField(".SomeWrongEntity")


class Secondary(models.Base):
    data = fields.IntField()


@pytest.mark.parametrize(
    ["model"],
    [
        (Primary,),
        (Third,),
        (Fourth,),
        (Fifth,),
        (Sixth,),
    ],
)
def test_embedded_model(model):
    entity = model()
    assert entity.secondary is None
    entity.name = "chuck"
    entity.secondary = Secondary()
    entity.secondary.data = 42

    with pytest.raises(errors.ValidationError):
        entity.secondary = "something different"

    entity.secondary = None


def test_relative_too_much():
    with pytest.raises(ValueError):
        Seventh()


def test_wrong_entity():
    with pytest.raises(ValueError):
        Eighth()


class File(models.Base):
    name = fields.StringField()
    size = fields.FloatField()


class Directory(models.Base):
    name = fields.StringField()
    children = fields.ListField(["Directory", File])


def test_list_field():
    directory = Directory()
    some_file = File()
    directory.children.append(some_file)
    sub_dir = Directory()
    directory.children.append(sub_dir)
    with pytest.raises(errors.ValidationError):
        directory.children.append("some string")
