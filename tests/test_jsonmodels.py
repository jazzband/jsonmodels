#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jsonmodels
----------------------------------

Tests for `jsonmodels` module.
"""

import unittest

from jsonmodels import models, fields, error


class TestJsonmodels(unittest.TestCase):

    def test_model1(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()

        alan = Person()
        alan.validate()

        alan.name = 'Alan'
        alan.surname = 'Wake'
        alan.age = 34
        alan.validate()

    def test_required(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField()
            age = fields.IntField()

        alan = Person()
        self.assertRaises(error.ValidationError, alan.validate)

        alan.name = 'Chuck'
        alan.validate()

    def test_type_validation(self):

        class Person(models.Base):

            name = fields.StringField()
            age = fields.IntField()

        alan = Person()
        alan.age = '42'
        self.assertRaises(error.ValidationError, alan.validate)

        alan.age = 42
        alan.validate()

    def test_base_validation(self):
        """BaseField should not be usable."""

        class Person(models.Base):

            name = fields.BaseField()

        alan = Person()
        self.assertRaises(error.ValidationError, alan.validate)

        alan.name = 'some name'
        self.assertRaises(error.ValidationError, alan.validate)

        alan.name = 2345
        self.assertRaises(error.ValidationError, alan.validate)

    def test_value_replacements(self):

        class Person(models.Base):

            name = fields.StringField()
            age = fields.IntField()
            cash = fields.FloatField()
            children = fields.ListField()

        alan = Person()
        self.assertIsNone(alan.name)
        self.assertIsNone(alan.age)
        self.assertIsNone(alan.cash)
        self.assertIsInstance(alan.children, list)

    def test_list_field(self):

        class Car(models.Base):

            wheels = fields.ListField()

        viper = Car()
        viper.validate()

        viper.wheels.append('some')
        viper.wheels.append('not necessarily')
        viper.wheels.append('proper')
        viper.wheels.append('wheels')
        viper.validate()

    def test_list_field_types(self):

        class Wheel(models.Base):
            pass

        class Wheel2(models.Base):
            pass

        class Car(models.Base):

            wheels = fields.ListField(items_types=[Wheel])

        viper = Car()
        viper.validate()

        viper.wheels.append(Wheel())
        viper.wheels.append(Wheel())
        viper.validate()

        viper.wheels.append(Wheel2)
        self.assertRaises(error.ValidationError, viper.validate)

    def test_list_field_for_subtypes(self):

        class Car(models.Base):
            pass

        class Viper(Car):
            pass

        class Lamborghini(Car):
            pass

        class Garage1(models.Base):

            cars = fields.ListField(items_types=[Car])

        garage = Garage1()
        garage.validate()

        garage.cars.append(Car())
        garage.validate()

        garage.cars.append(Viper())
        garage.cars.append(Lamborghini())
        garage.validate()

        class Garage2(models.Base):

            cars = fields.ListField(items_types=[Viper, Lamborghini])

        garage = Garage2()
        garage.validate()

        garage.cars.append(Viper())
        garage.cars.append(Lamborghini())
        garage.validate()

        garage.cars.append(Car())
        self.assertRaises(error.ValidationError, garage.validate)

    def test_list_validation(self):

        class Garage(models.Base):

            cars = fields.ListField()

        garage = Garage()
        garage.validate()

        garage.cars = 'some string'
        self.assertRaises(error.ValidationError, garage.validate)

if __name__ == '__main__':
    unittest.main()
