from jsonmodels.fields import DictField, EmbeddedField, ListField, StringField
from jsonmodels.models import Base


class Nullable(Base):
    field = StringField(nullable=True)


class NullableDict(Base):
    field = DictField(nullable=True)


class NullableListField(Base):
    field = ListField([str], nullable=True)


class NullableEmbedded(Base):
    field = EmbeddedField(Nullable, nullable=True)


def test_nullable_simple_field():
    result = Nullable.to_json_schema()

    assert result["properties"]["field"]["type"] == ["string", "null"]


def test_nullable_dict_field():
    result = NullableDict.to_json_schema()

    assert result["properties"]["field"]["type"] == ["object", "null"]


def test_nullable_list_field():
    result = NullableListField.to_json_schema()
    items = result["properties"]["field"]["items"]
    assert items.get("oneOf")
    assert items["oneOf"] == [{"type": "string"}, {"type": "null"}]


def test_nullable_embedded_field():
    result = NullableEmbedded.to_json_schema()

    expected = [
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {"field": {"type": ["string", "null"]}},
        },
        {"type": "null"},
    ]
    assert result["properties"]["field"]["oneOf"] == expected
