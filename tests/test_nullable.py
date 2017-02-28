from jsonmodels.fields import StringField, ListField, EmbeddedField
from jsonmodels.models import Base


class Nullable(Base):
    field = StringField(nullable=True)


class NullableListField(Base):
    field = ListField([str], nullable=True)


class NullableEmbedded(Base):
    field = EmbeddedField(Nullable, nullable=True)


def test_nullable_simple_field():
    result = Nullable.to_json_schema()

    assert result['properties']['field']['type'] == ['string', 'null']


def test_nullable_list_field():
    result = NullableListField.to_json_schema()

    assert result['properties']['field']['type'] == ['array', 'null']


def test_nullable_embedded_field():
    result = NullableEmbedded.to_json_schema()

    assert result['properties']['field']['type'] == ['object', 'null']

    field = result['properties']['field']

    assert field['properties']['field']['type'] == ['string', 'null']
