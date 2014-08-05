"""Tests for casting to structure."""

import unittest
from datetime import datetime

from jsonmodels import models, fields, errors


class _DateField(fields.BaseField):

    _types = (datetime,)


class TestToStructMethod(unittest.TestCase):

    def test_to_struct_basic(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            cash = fields.FloatField()

        alan = Person()
        self.assertRaises(errors.ValidationError, alan.to_struct)

        alan.name = 'Alan'
        alan.surname = 'Wake'
        self.assertEqual({'name': 'Alan', 'surname': 'Wake'}, alan.to_struct())

        alan.age = 24
        alan.cash = 2445.45

        pattern = {
            'name': 'Alan',
            'surname': 'Wake',
            'age': 24,
            'cash': 2445.45,
        }

        self.assertEqual(pattern, alan.to_struct())

    def test_to_struct_nested_1(self):

        class Car(models.Base):

            brand = fields.StringField()

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField(Car)

        place = ParkingPlace()
        place.location = 'never never land'

        pattern = {
            'location': 'never never land',
        }
        self.assertEqual(pattern, place.to_struct())

        place.car = Car()
        pattern['car'] = {}
        self.assertEqual(pattern, place.to_struct())

        place.car.brand = 'Fiat'
        pattern['car']['brand'] = 'Fiat'
        self.assertEqual(pattern, place.to_struct())

    def test_to_struct_nested_2(self):

        class Viper(models.Base):

            serial = fields.StringField()

        class Lamborghini(models.Base):

            serial = fields.StringField()

        class Parking(models.Base):

            location = fields.StringField()
            cars = fields.ListField([Viper, Lamborghini])

        parking = Parking()
        pattern = {'cars': []}
        self.assertEqual(pattern, parking.to_struct())

        parking.location = 'somewhere'
        pattern['location'] = 'somewhere'
        self.assertEqual(pattern, parking.to_struct())

        v = Viper()
        v.serial = '12345'
        parking.cars.append(v)
        pattern['cars'].append({'serial': '12345'})
        self.assertEqual(pattern, parking.to_struct())

        parking.cars.append(Viper())
        pattern['cars'].append({})
        self.assertEqual(pattern, parking.to_struct())

        l = Lamborghini()
        l.serial = '54321'
        parking.cars.append(l)
        pattern['cars'].append({'serial': '54321'})
        self.assertEqual(pattern, parking.to_struct())

    def test_to_struct_with_non_models_types(self):

        class Person(models.Base):

            names = fields.ListField(str)
            surname = fields.StringField()

        person = Person()
        pattern = {'names': []}

        self.assertEqual(pattern, person.to_struct())

        person.surname = 'Norris'
        pattern['surname'] = 'Norris'
        person.validate()
        self.assertEqual(pattern, person.to_struct())

        person.names.append('Chuck')
        pattern['names'].append('Chuck')
        person.validate()
        self.assertEqual(pattern, person.to_struct())

        person.names.append('Testa')
        pattern['names'].append('Testa')
        person.validate()
        self.assertEqual(pattern, person.to_struct())

    def test_to_struct_with_multi_non_models_types(self):

        class Person(models.Base):

            name = fields.StringField()
            mix = fields.ListField((str, float))

        person = Person()
        pattern = {'mix': []}
        person.validate()
        self.assertEqual(pattern, person.to_struct())

        person.mix.append('something')
        pattern['mix'].append('something')
        person.validate()
        self.assertEqual(pattern, person.to_struct())

        person.mix.append(42.0)
        pattern['mix'].append(42.0)
        person.validate()
        self.assertEqual(pattern, person.to_struct())

        person.mix.append('different')
        pattern['mix'].append('different')
        person.validate()
        self.assertEqual(pattern, person.to_struct())
