"""Tests for fields."""

import unittest

from jsonmodels import models, fields


class TestFields(unittest.TestCase):

    def test_bool_field(self):

        field = fields.BoolField()

        class Person(models.Base):

            is_programmer = field

        person = Person()
        self.assertIsNone(person.is_programmer)

        person.is_programmer = True
        self.assertTrue(person.is_programmer)

        person.is_programmer = False
        self.assertFalse(person.is_programmer)

        self.assertIs(field.parse_value(True), True)
        self.assertIs(field.parse_value('something'), True)
        self.assertIs(field.parse_value(object()), True)

        self.assertIsNone(field.parse_value(None))

        self.assertIs(field.parse_value(False), False)
        self.assertIs(field.parse_value(0), False)
        self.assertIs(field.parse_value(''), False)
        self.assertIs(field.parse_value([]), False)
