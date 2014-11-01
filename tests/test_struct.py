from datetime import datetime

import pytest

from jsonmodels import models, fields, errors


class _DateField(fields.BaseField):

    _types = (datetime,)


def test_to_struct_basic():

    class Person(models.Base):

        name = fields.StringField(required=True)
        surname = fields.StringField(required=True)
        age = fields.IntField()
        cash = fields.FloatField()

    alan = Person()
    with pytest.raises(errors.ValidationError):
        alan.to_struct()

    alan.name = 'Alan'
    alan.surname = 'Wake'
    assert {'name': 'Alan', 'surname': 'Wake'} == alan.to_struct()

    alan.age = 24
    alan.cash = 2445.45

    pattern = {
        'name': 'Alan',
        'surname': 'Wake',
        'age': 24,
        'cash': 2445.45,
    }

    assert pattern == alan.to_struct()


def test_to_struct_nested_1():

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
    assert pattern == place.to_struct()

    place.car = Car()
    pattern['car'] = {}
    assert pattern == place.to_struct()

    place.car.brand = 'Fiat'
    pattern['car']['brand'] = 'Fiat'
    assert pattern == place.to_struct()


def test_to_struct_nested_2():

    class Viper(models.Base):

        serial = fields.StringField()

    class Lamborghini(models.Base):

        serial = fields.StringField()

    class Parking(models.Base):

        location = fields.StringField()
        cars = fields.ListField([Viper, Lamborghini])

    parking = Parking()
    pattern = {'cars': []}
    assert pattern == parking.to_struct()

    parking.location = 'somewhere'
    pattern['location'] = 'somewhere'
    assert pattern == parking.to_struct()

    v = Viper()
    v.serial = '12345'
    parking.cars.append(v)
    pattern['cars'].append({'serial': '12345'})
    assert pattern == parking.to_struct()

    parking.cars.append(Viper())
    pattern['cars'].append({})
    assert pattern == parking.to_struct()

    l = Lamborghini()
    l.serial = '54321'
    parking.cars.append(l)
    pattern['cars'].append({'serial': '54321'})
    assert pattern == parking.to_struct()


def test_to_struct_with_non_models_types():

    class Person(models.Base):

        names = fields.ListField(str)
        surname = fields.StringField()

    person = Person()
    pattern = {'names': []}

    assert pattern == person.to_struct()

    person.surname = 'Norris'
    pattern['surname'] = 'Norris'
    assert pattern == person.to_struct()

    person.names.append('Chuck')
    pattern['names'].append('Chuck')
    assert pattern == person.to_struct()

    person.names.append('Testa')
    pattern['names'].append('Testa')
    pattern == person.to_struct()


def test_to_struct_with_multi_non_models_types():

    class Person(models.Base):

        name = fields.StringField()
        mix = fields.ListField((str, float))

    person = Person()
    pattern = {'mix': []}
    assert pattern == person.to_struct()

    person.mix.append('something')
    pattern['mix'].append('something')
    assert pattern == person.to_struct()

    person.mix.append(42.0)
    pattern['mix'].append(42.0)
    assert pattern == person.to_struct()

    person.mix.append('different')
    pattern['mix'].append('different')
    assert pattern == person.to_struct()
