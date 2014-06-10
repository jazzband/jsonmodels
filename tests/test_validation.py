"""Test for validators."""

import unittest
from mock import Mock

from jsonmodels import models, fields


class TestValidation(unittest.TestCase):

    def test_validation(self):

        validator1 = Mock()
        validator2 = Mock()
        validator3 = Mock()

        class Person(models.Base):

            name = fields.StringField(
                required=True, validators=[validator1, validator2])
            surname = fields.StringField(required=True)
            age = fields.IntField(validators=validator3)
            cash = fields.FloatField()

        person = Person()
        person.name = 'John'
        person.surname = 'Smith'
        person.age = 33
        person.cash = 123567.89

        person.validate()

        validator1.validate.assert_called_once_with('John')
        validator2.validate.assert_called_once_with('John')
        validator3.validate.assert_called_once_with(33)
