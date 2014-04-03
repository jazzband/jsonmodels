"""Tests for `jsonmodels` module."""

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

    def test_embedded_model(self):

        class Secondary(models.Base):

            data = fields.IntField()

        class Primary(models.Base):

            name = fields.StringField()
            secondary = fields.EmbeddedField(Secondary)

        entity = Primary()
        entity.validate()
        self.assertIsNone(entity.secondary)

        entity.name = 'chuck'
        entity.validate()

        entity.secondary = Secondary()
        entity.validate()

        entity.secondary.data = 42
        entity.validate()

        entity.secondary.data = '42'
        self.assertRaises(error.ValidationError, entity.validate)

        entity.secondary.data = 42
        entity.validate()

        entity.secondary = 'something different'
        self.assertRaises(error.ValidationError, entity.validate)

        entity.secondary = None
        entity.validate()

    def test_embedded_required_validation(self):

        class Secondary(models.Base):

            data = fields.IntField(required=True)

        class Primary(models.Base):

            name = fields.StringField()
            secondary = fields.EmbeddedField(Secondary)

        entity = Primary()
        sec = Secondary()
        sec.data = 33
        entity.secondary = sec
        entity.validate()
        entity.secondary.data = None
        self.assertRaises(error.ValidationError, entity.validate)

        entity.secondary = None
        entity.validate()

        class Primary(models.Base):

            name = fields.StringField()
            secondary = fields.EmbeddedField(Secondary, required=True)

        entity = Primary()
        sec = Secondary()
        sec.data = 33
        entity.secondary = sec
        entity.validate()
        entity.secondary.data = None
        self.assertRaises(error.ValidationError, entity.validate)

    def test_embedded_inheritance(self):

        class Car(models.Base):
            pass

        class Viper(Car):
            pass

        class Lamborghini(Car):
            pass

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField([Viper, Lamborghini])

        place = ParkingPlace()

        place.car = Viper()
        place.validate()

        place.car = Lamborghini()
        place.validate()

        place.car = Car()
        self.assertRaises(error.ValidationError, place.validate)

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField(Car)

        place = ParkingPlace()

        place.car = Viper()
        place.validate()

        place.car = Lamborghini()
        place.validate()

        place.car = Car()
        place.validate()

    def test_to_struct_basic(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()
            cash = fields.FloatField()

        alan = Person()
        self.assertRaises(error.ValidationError, alan.to_struct)

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

    def test_iterable(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()
            cash = fields.FloatField()

        alan = Person()

        alan.name = 'Alan'
        alan.surname = 'Wake'
        alan.age = 24
        alan.cash = 2445.45

        pattern = {
            'name': 'Alan',
            'surname': 'Wake',
            'age': 24,
            'cash': 2445.45,
        }

        result = {}
        for name, value in alan:
            result[name] = value

        self.assertEqual(pattern, result)

    def test_get_field(self):

        name_field = fields.StringField()
        surname_field = fields.StringField()
        age_field = fields.IntField()

        class Person(models.Base):

            name = name_field
            surname = surname_field
            age = age_field

        alan = Person()

        self.assertIs(alan.get_field('name'), name_field)
        self.assertIs(alan.get_field('surname'), surname_field)
        self.assertIs(alan.get_field('age'), age_field)
