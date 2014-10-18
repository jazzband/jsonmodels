import unittest

from jsonmodels import models, fields, errors


class TestJsonmodelsInitialization(unittest.TestCase):

    def test_initialization(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()
            cash = fields.FloatField()

        data = dict(
            name='Alan',
            surname='Wake',
            age=24,
            cash=2445.45,
            trash='123qwe',
        )

        alan1 = Person(**data)
        alan2 = Person()
        alan2.populate(**data)
        for alan in [alan1, alan2]:
            self.assertEqual(alan.name, 'Alan')
            self.assertEqual(alan.surname, 'Wake')
            self.assertEqual(alan.age, 24)
            self.assertEqual(alan.cash, 2445.45)

            self.assertTrue(not hasattr(alan, 'trash'))

    def test_deep_initialization(self):

        class Car(models.Base):

            brand = fields.StringField()

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField(Car)

        data = {
            'location': 'somewhere',
            'car': {
                'brand': 'awesome brand'
            }
        }

        parking1 = ParkingPlace(**data)
        parking2 = ParkingPlace()
        parking2.populate(**data)
        for parking in [parking1, parking2]:
            self.assertEqual(parking.location, 'somewhere')
            car = parking.car
            self.assertTrue(isinstance(car, Car))
            self.assertEqual(car.brand, 'awesome brand')

            self.assertEqual(parking.location, 'somewhere')
            car = parking.car
            self.assertTrue(isinstance(car, Car))
            self.assertEqual(car.brand, 'awesome brand')

    def test_deep_initialization_error_with_multitypes(self):

        class Viper(models.Base):

            brand = fields.StringField()

        class Lamborghini(models.Base):

            brand = fields.StringField()

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField([Viper, Lamborghini])

        data = {
            'location': 'somewhere',
            'car': {
                'brand': 'awesome brand'
            }
        }

        self.assertRaises(errors.ValidationError, ParkingPlace, **data)

        place = ParkingPlace()
        self.assertRaises(errors.ValidationError, place.populate, **data)

    def test_deep_initialization_with_list(self):

        class Car(models.Base):

            brand = fields.StringField()

        class Parking(models.Base):

            location = fields.StringField()
            cars = fields.ListField(items_types=Car)

        data = {
            'location': 'somewhere',
            'cars': [
                {
                    'brand': 'one',
                },
                {
                    'brand': 'two',
                },
                {
                    'brand': 'three',
                },
            ],
        }

        parking1 = Parking(**data)
        parking2 = Parking()
        parking2.populate(**data)
        for parking in [parking1, parking2]:
            self.assertEqual(parking.location, 'somewhere')
            cars = parking.cars
            self.assertTrue(isinstance(cars, list))
            self.assertEqual(len(cars), 3)

            values = []
            for car in cars:
                self.assertIsInstance(car, Car)
                values.append(car.brand)
            self.assertTrue('one' in values)
            self.assertTrue('two' in values)
            self.assertTrue('three' in values)

    def test_deep_initialization_error_with_list_and_multitypes(self):

        class Viper(models.Base):

            brand = fields.StringField()

        class Lamborghini(models.Base):

            brand = fields.StringField()

        class Parking(models.Base):

            location = fields.StringField()
            cars = fields.ListField([Viper, Lamborghini])

        data = {
            'location': 'somewhere',
            'cars': [
                {
                    'brand': 'one',
                },
                {
                    'brand': 'two',
                },
                {
                    'brand': 'three',
                },
            ],
        }

        self.assertRaises(errors.ValidationError, Parking, **data)

        parking = Parking()
        self.assertRaises(errors.ValidationError, parking.populate, **data)

        # Case for not iterable data.
        data = {
            'location': 'somewhere',
            'cars': object(),
        }

        self.assertRaises(errors.ValidationError, Parking, **data)

        parking = Parking()
        self.assertRaises(errors.ValidationError, parking.populate, **data)

    def test_initialization_with_non_models_types(self):

        class Person(models.Base):

            names = fields.ListField(str)
            surname = fields.StringField()

        data = {
            'names': ['Chuck', 'Testa'],
            'surname': 'Norris'
        }

        person1 = Person(**data)
        person2 = Person()
        person2.populate(**data)

        for person in [person1, person2]:
            self.assertEqual(person.surname, 'Norris')
            self.assertEqual(len(person.names), 2)
            self.assertIn('Chuck', person.names)
            self.assertIn('Testa', person.names)

    def test_initialization_with_multi_non_models_types(self):

        class Person(models.Base):

            name = fields.StringField()
            mix = fields.ListField((str, float))

        data = {
            'name': 'Chuck',
            'mix': ['something', 42.0, 'weird']
        }

        person1 = Person(**data)
        person2 = Person()
        person2.populate(**data)

        for person in [person1, person2]:
            self.assertEqual(person.name, 'Chuck')
            self.assertEqual(len(person.mix), 3)
            self.assertIn('something', person.mix)
            self.assertIn(42.0, person.mix)
            self.assertIn('weird', person.mix)

    def test_deep_initialization_for_embed_field(self):

        class Car(models.Base):

            brand = fields.StringField()

        class ParkingPlace(models.Base):

            location = fields.StringField()
            car = fields.EmbeddedField(Car)

        data = {
            'location': 'somewhere',
            'car': Car(brand='awesome brand'),
        }

        parking1 = ParkingPlace(**data)
        parking2 = ParkingPlace()
        parking2.populate(**data)
        for parking in [parking1, parking2]:
            self.assertEqual(parking.location, 'somewhere')
            car = parking.car
            self.assertTrue(isinstance(car, Car))
            self.assertEqual(car.brand, 'awesome brand')

            self.assertEqual(parking.location, 'somewhere')
            car = parking.car
            self.assertTrue(isinstance(car, Car))
            self.assertEqual(car.brand, 'awesome brand')
