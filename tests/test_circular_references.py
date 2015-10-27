from jsonmodels import models, fields


class Primary(models.Base):

    name = fields.StringField()
    secondary = fields.EmbeddedField('Secondary')


class Secondary(models.Base):

    data = fields.IntField()
    first = fields.EmbeddedField('Primary')


def test_generate_circular_schema():
    Primary.to_json_schema()
