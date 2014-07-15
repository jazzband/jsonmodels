"""Test for validators."""

import unittest

from jsonmodels import models, fields, validators, error


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

    def test_validators_are_always_iterable(self):

        class Person(models.Base):

            children = fields.ListField()

        alan = Person()

        self.assertTrue(
            isinstance(alan.get_field('children').validators, list))


class TestMinValidator(unittest.TestCase):

    def test_validation(self):

        validator = validators.Min(3)
        self.assertEqual(3, validator.minimum_value)

        validator.validate(4)
        validator.validate(3)
        self.assertRaises(error.ValidationError, validator.validate, 2)
        self.assertRaises(error.ValidationError, validator.validate, -2)

    def test_exclusive_validation(self):

        validator = validators.Min(3, True)
        self.assertEqual(3, validator.minimum_value)

        validator.validate(4)
        self.assertRaises(error.ValidationError, validator.validate, 3)
        self.assertRaises(error.ValidationError, validator.validate, 2)
        self.assertRaises(error.ValidationError, validator.validate, -2)


class TestMaxValidator(unittest.TestCase):

    def test_validation(self):

        validator = validators.Max(42)
        self.assertEqual(42, validator.maximum_value)

        validator.validate(4)
        validator.validate(42)
        self.assertRaises(error.ValidationError, validator.validate, 42.01)
        self.assertRaises(error.ValidationError, validator.validate, 43)

    def test_exclusive_validation(self):

        validator = validators.Max(42, True)
        self.assertEqual(42, validator.maximum_value)

        validator.validate(4)
        self.assertRaises(error.ValidationError, validator.validate, 42)
        self.assertRaises(error.ValidationError, validator.validate, 42.01)
        self.assertRaises(error.ValidationError, validator.validate, 43)
