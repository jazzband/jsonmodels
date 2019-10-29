from unittest import mock

from jsonmodels import fields


@mock.patch('jsonmodels.fields.BaseField.to_struct')
def test_toPlain_calls_to_struct(f):
    """Test if default implementation of toPlain calls to_struct."""
    field = fields.StringField()
    field.toPlain(value="text")
    f.assert_called_once()
