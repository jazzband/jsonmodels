"""Test for validators."""

import unittest

from jsonmodels import models, fields, validators, errors


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
        self.assertRaises(errors.ValidationError, validator.validate, 2)
        self.assertRaises(errors.ValidationError, validator.validate, -2)

    def test_exclusive_validation(self):

        validator = validators.Min(3, True)
        self.assertEqual(3, validator.minimum_value)

        validator.validate(4)
        self.assertRaises(errors.ValidationError, validator.validate, 3)
        self.assertRaises(errors.ValidationError, validator.validate, 2)
        self.assertRaises(errors.ValidationError, validator.validate, -2)


class TestMaxValidator(unittest.TestCase):

    def test_validation(self):

        validator = validators.Max(42)
        self.assertEqual(42, validator.maximum_value)

        validator.validate(4)
        validator.validate(42)
        self.assertRaises(errors.ValidationError, validator.validate, 42.01)
        self.assertRaises(errors.ValidationError, validator.validate, 43)

    def test_exclusive_validation(self):

        validator = validators.Max(42, True)
        self.assertEqual(42, validator.maximum_value)

        validator.validate(4)
        self.assertRaises(errors.ValidationError, validator.validate, 42)
        self.assertRaises(errors.ValidationError, validator.validate, 42.01)
        self.assertRaises(errors.ValidationError, validator.validate, 43)


class TestRegexValidator(unittest.TestCase):

    def test_validation(self):

        validator = validators.Regex('some')
        self.assertEqual('some', validator.pattern)

        validator.validate('some string')
        validator.validate('get some chips')
        self.assertRaises(errors.ValidationError, validator.validate, 'asdf')
        self.assertRaises(
            errors.ValidationError, validator.validate, 'trololo')

    def test_validation_2(self):

        validator = validators.Regex('^some[0-9]$')
        self.assertEqual('^some[0-9]$', validator.pattern)

        validator.validate('some0')
        self.assertRaises(errors.ValidationError, validator.validate, 'some')
        self.assertRaises(errors.ValidationError, validator.validate, ' some')
        self.assertRaises(errors.ValidationError, validator.validate, 'asdf')
        self.assertRaises(
            errors.ValidationError, validator.validate, 'trololo')

    def test_validation_ignorecase(self):
        validator = validators.Regex('^some$')
        validator.validate('some')
        self.assertRaises(errors.ValidationError, validator.validate, 'sOmE')

        validator = validators.Regex('^some$', ignorecase=True)
        validator.validate('some')
        validator.validate('SoMe')

    def test_validation_multiline(self):
        validator = validators.Regex('^s.*e$')
        validator.validate('some')
        self.assertRaises(
            errors.ValidationError, validator.validate, 'some\nso more')

        validator = validators.Regex('^s.*e$', multiline=True)
        validator.validate('some')
        validator.validate('some\nso more')

    def test_regex_validator(self):

        class Person(models.Base):

            name = fields.StringField(
                validators=validators.Regex('^[a-z]+$', ignorecase=True))

        person = Person()

        def assign():
            person.name = '123'
        self.assertRaises(errors.ValidationError, assign)

        person.name = 'Jimmy'

    def test_regex_validator_when_ecma_regex_given(self):

        class Person(models.Base):

            name = fields.StringField(
                validators=validators.Regex('/^[a-z]+$/i', ignorecase=False))

        person = Person()

        def assign():
            person.name = '123'
        self.assertRaises(errors.ValidationError, assign)

        person.name = 'Jimmy'


class TestLengthValidator(unittest.TestCase):

    def test_init(self):
        validator = validators.Length(0, 10)
        self.assertEqual(0, validator.minimum_value)
        self.assertEqual(10, validator.maximum_value)

        validator = validators.Length(0)
        self.assertEqual(0, validator.minimum_value)
        self.assertIsNone(validator.maximum_value)

        validator = validators.Length(maximum_value=10)
        self.assertEqual(10, validator.maximum_value)
        self.assertIsNone(validator.minimum_value)

        self.assertRaises(ValueError, validators.Length)

    def test_validation(self):
        validator = validators.Length(1, 10)
        validator.validate('word')
        validator.validate('w' * 10)
        validator.validate('w')
        validator.validate([1, 2, 3])

        self.assertRaises(errors.ValidationError, validator.validate, '')
        self.assertRaises(
            errors.ValidationError, validator.validate, 'na' * 10)
