"""Tests for JSON schema generation."""

import unittest

from jsonmodels import models, fields
from .utils import get_fixture, compare_schemas


class TestJsonmodels(unittest.TestCase):

    def test_model1(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()

        alan = Person()
        schema = alan.to_json_schema()

        pattern = get_fixture('schema1.json')

        self.assertTrue(compare_schemas(pattern, schema))

    def test_model2(self):

        class Car(models.Base):

            brand = fields.StringField(required=True)
            registration = fields.StringField(required=True)

        class Toy(models.Base):

            name = fields.StringField(required=True)

        class Kid(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            toys = fields.ListField(Toy)

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            kids = fields.ListField(Kid)
            car = fields.EmbeddedField(Car)

        chuck = Person()
        schema = chuck.to_json_schema()

        pattern = get_fixture('schema2.json')
        self.assertTrue(compare_schemas(pattern, schema))
