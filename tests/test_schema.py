"""Tests for JSON schema generation."""

import unittest

from jsonmodels import models, fields
from jsonmodels.utils import compare_schemas

from .utils import get_fixture


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

    def test_model3(self):

        class Viper(models.Base):

            brand = fields.StringField()
            capacity = fields.FloatField()

        class Lamborghini(models.Base):

            brand = fields.StringField()
            velocity = fields.FloatField()

        class PC(models.Base):

            name = fields.StringField()
            ports = fields.StringField()

        class Laptop(models.Base):

            name = fields.StringField()
            battery_voltage = fields.FloatField()

        class Tablet(models.Base):

            name = fields.StringField()
            os = fields.StringField()

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            car = fields.EmbeddedField([Viper, Lamborghini])
            computer = fields.ListField([PC, Laptop, Tablet])

        chuck = Person()
        schema = chuck.to_json_schema()

        pattern = get_fixture('schema3.json')
        self.assertTrue(compare_schemas(pattern, schema))

    def test_model_with_constructors(self):

        class Car(models.Base):

            def __init__(self, some_value):
                pass

            brand = fields.StringField(required=True)
            registration = fields.StringField(required=True)

        class Toy(models.Base):

            def __init__(self, some_value):
                pass

            name = fields.StringField(required=True)

        class Kid(models.Base):

            def __init__(self, some_value):
                pass

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            toys = fields.ListField(Toy)

        class Person(models.Base):

            def __init__(self, some_value):
                pass

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            kids = fields.ListField(Kid)
            car = fields.EmbeddedField(Car)

        schema = Person.to_json_schema()

        pattern = get_fixture('schema2.json')
        self.assertTrue(compare_schemas(pattern, schema))

    def test_datetime_fields(self):

        class Event(models.Base):

            time = fields.TimeField()
            date = fields.DateField()
            end = fields.DateTimeField()

        schema = Event.to_json_schema()

        pattern = get_fixture('schema4.json')
        self.assertTrue(compare_schemas(pattern, schema))

    def test_bool_field(self):

        class Person(models.Base):

            has_childen = fields.BoolField()

        schema = Person.to_json_schema()

        pattern = get_fixture('schema5.json')
        self.assertTrue(compare_schemas(pattern, schema))
