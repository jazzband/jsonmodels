from jsonmodels import fields, models
from jsonmodels.utilities import compare_schemas

from .utilities import get_fixture


class Primary(models.Base):
    name = fields.StringField()
    secondary = fields.EmbeddedField("Secondary")


class Secondary(models.Base):
    data = fields.IntField()
    first = fields.EmbeddedField("Primary")


def test_generate_circular_schema():
    schema = Primary.to_json_schema()

    pattern = get_fixture("schema_circular.json")
    assert compare_schemas(pattern, schema) is True


class File(models.Base):
    name = fields.StringField()
    size = fields.FloatField()


class Directory(models.Base):
    name = fields.StringField()
    children = fields.ListField(["Directory", File])


class Filesystem(models.Base):
    name = fields.StringField()
    children = fields.ListField([Directory, File])


def test_generate_circular_schema2():
    schema = Filesystem.to_json_schema()

    pattern = get_fixture("schema_circular2.json")
    assert compare_schemas(pattern, schema) is True
