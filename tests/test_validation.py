"""Test for validators."""

import unittest

from jsonmodels import models, fields


class FakeValidator(object):

    def __init__(self):
        self.called_with = None
        self.called_amount = 0

    def validate(self, value):
        self.called_amount = self.called_amount + 1
        self.called_with = value

    def assert_called_once_with(self, value):
        if value != self.called_with or self.called_amount != 1:
            raise AssertionError('Assert called once with "{}" failed!')


class TestValidation(unittest.TestCase):

    def test_validation(self):

        validator1 = FakeValidator()
        validator2 = FakeValidator()

        called = []
        arg = []

        def validator3(value):
            called.append(1)
            arg.append(value)

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

        validator1.assert_called_once_with('John')
        validator2.assert_called_once_with('John')

        self.assertEqual(1, sum(called))
        self.assertEqual(33, arg.pop())
