"""Tests for `jsonmodels` module."""

import unittest

from jsonmodels import models, fields, errors


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
        self.assertRaises(errors.ValidationError, alan.validate)

        alan.name = 'Chuck'
        alan.validate()

    def test_type_validation(self):

        class Person(models.Base):

            name = fields.StringField()
            age = fields.IntField()

        alan = Person()
        alan.age = '42'
        self.assertRaises(errors.ValidationError, alan.validate)

        alan.age = 42
        alan.validate()

    def test_base_validation(self):
        """BaseField should not be usable."""

        class Person(models.Base):

            name = fields.BaseField()

        alan = Person()
        self.assertRaises(errors.ValidationError, alan.validate)

        alan.name = 'some name'
        self.assertRaises(errors.ValidationError, alan.validate)

        alan.name = 2345
        self.assertRaises(errors.ValidationError, alan.validate)

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
        self.assertRaises(errors.ValidationError, viper.validate)

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
        self.assertRaises(errors.ValidationError, garage.validate)

    def test_list_validation(self):

        class Garage(models.Base):

            cars = fields.ListField()

        garage = Garage()
        garage.validate()

        garage.cars = 'some string'
        self.assertRaises(errors.ValidationError, garage.validate)

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
        self.assertRaises(errors.ValidationError, entity.validate)

        entity.secondary.data = 42
        entity.validate()

        entity.secondary = 'something different'
        self.assertRaises(errors.ValidationError, entity.validate)

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
        self.assertRaises(errors.ValidationError, entity.validate)

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
        self.assertRaises(errors.ValidationError, entity.validate)

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
        self.assertRaises(errors.ValidationError, place.validate)

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

    def test_repr(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()

        chuck = Person()

        self.assertEqual(chuck.__repr__(), '<Person: Person object>')
        self.assertEqual(chuck.__str__(), 'Person object')

        class Person2(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()

            def __str__(self):
                return self.name

        chuck = Person2()

        self.assertEqual(chuck.__repr__(), '<Person2: >')

        chuck.name = 'Chuck'
        self.assertEqual(chuck.__repr__(), '<Person2: Chuck>')
        self.assertEqual(chuck.__str__(), 'Chuck')

        chuck.name = 'Testa'
        self.assertEqual(chuck.__repr__(), '<Person2: Testa>')
        self.assertEqual(chuck.__str__(), 'Testa')

    def test_list_field_with_non_model_types(self):

        class Person(models.Base):

            names = fields.ListField(str)
            surname = fields.StringField()

        person = Person(surname='Norris')
        person.names.append('Chuck')
        person.names.append('Testa')

        person.validate()

    def test_help_text(self):

        class Person(models.Base):

            name = fields.StringField(help_text='Name of person.')
            age = fields.IntField(help_text='Age of person.')

        person = Person()
        self.assertEqual(person.get_field('name').help_text, 'Name of person.')
        self.assertEqual(person.get_field('age').help_text, 'Age of person.')

    def test_types(self):

        class Person(object):
            pass

        class Person2(object):
            pass

        allowed_types = (Person,)

        field = fields.EmbeddedField(allowed_types)
        self.assertEqual(allowed_types, field.types)

        allowed_types = (Person, Person2)

        field = fields.EmbeddedField(allowed_types)
        self.assertEqual(allowed_types, field.types)

    def test_items_types(self):

        class Person(object):
            pass

        class Person2(object):
            pass

        allowed_types = (Person,)

        field = fields.ListField(allowed_types)
        self.assertEqual(allowed_types, field.items_types)

        allowed_types = (Person, Person2)

        field = fields.ListField(allowed_types)
        self.assertEqual(allowed_types, field.items_types)

        field = fields.ListField()
        self.assertEqual(tuple(), field.items_types)

    def test_required_embedded_field(self):

        class Secondary(models.Base):

            data = fields.IntField()

        class Primary(models.Base):

            name = fields.StringField()
            secondary = fields.EmbeddedField(Secondary, required=True)

        entity = Primary()
        self.assertRaises(errors.ValidationError, entity.validate)

        entity.secondary = Secondary()
        entity.validate()

        class Primary(models.Base):

            name = fields.StringField()
            secondary = fields.EmbeddedField(Secondary, required=False)

        entity = Primary()
        entity.secondary = None
        entity.validate()

    def test_required_list(self):

        class Wheel(models.Base):
            pass

        class Car(models.Base):

            wheels = fields.ListField(items_types=[Wheel], required=False)

        viper = Car()
        viper.validate()

        viper.wheels = None
        viper.validate()

        viper.wheels = [Wheel()]
        viper.validate()

        class Car(models.Base):

            wheels = fields.ListField(items_types=[Wheel], required=True)

        viper = Car()
        viper.validate()

        viper.wheels = None
        viper.validate()

        viper.wheels = [Wheel()]
        viper.validate()
