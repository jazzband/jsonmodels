from datetime import datetime

import pytest

from jsonmodels import errors, fields, models


class _DateField(fields.BaseField):
    _types = (datetime,)


def test_to_struct_basic():
    class Person(models.Base):
        name = fields.StringField(required=True)
        surname = fields.StringField(required=True)
        age = fields.IntField()
        cash = fields.FloatField()
        extra = fields.DictField()

    alan = Person()
    with pytest.raises(errors.ValidationError):
        alan.to_struct()

    alan.name = "Alan"
    alan.surname = "Wake"
    assert {"name": "Alan", "surname": "Wake"} == alan.to_struct()

    alan.age = 24
    alan.cash = 2445.45
    alan.extra = {"extra_value": 1}

    pattern = {
        "name": "Alan",
        "surname": "Wake",
        "age": 24,
        "cash": 2445.45,
        "extra": {"extra_value": 1},
    }

    assert pattern == alan.to_struct()


def test_to_struct_nested_1():
    class Car(models.Base):
        brand = fields.StringField()
        extra = fields.DictField()

    class ParkingPlace(models.Base):
        location = fields.StringField()
        car = fields.EmbeddedField(Car)

    place = ParkingPlace()
    place.location = "never never land"

    pattern = {
        "location": "never never land",
    }
    assert pattern == place.to_struct()

    place.car = Car()
    pattern["car"] = {}
    assert pattern == place.to_struct()

    place.car.brand = "Fiat"
    place.car.extra = {"extra": 1}
    pattern["car"]["brand"] = "Fiat"
    pattern["car"]["extra"] = {"extra": 1}
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
    pattern = {"cars": []}
    assert pattern == parking.to_struct()

    parking.location = "somewhere"
    pattern["location"] = "somewhere"
    assert pattern == parking.to_struct()

    viper = Viper()
    viper.serial = "12345"
    parking.cars.append(viper)
    pattern["cars"].append({"serial": "12345"})
    assert pattern == parking.to_struct()

    parking.cars.append(Viper())
    pattern["cars"].append({})
    assert pattern == parking.to_struct()

    lamborghini = Lamborghini()
    lamborghini.serial = "54321"
    parking.cars.append(lamborghini)
    pattern["cars"].append({"serial": "54321"})
    assert pattern == parking.to_struct()


def test_to_struct_with_non_models_types():
    class Person(models.Base):
        names = fields.ListField(str)
        surname = fields.StringField()

    person = Person()
    pattern = {"names": []}

    assert pattern == person.to_struct()

    person.surname = "Norris"
    pattern["surname"] = "Norris"
    assert pattern == person.to_struct()

    person.names.append("Chuck")
    pattern["names"].append("Chuck")
    assert pattern == person.to_struct()

    person.names.append("Testa")
    pattern["names"].append("Testa")
    pattern == person.to_struct()


def test_to_struct_with_multi_non_models_types():
    class Person(models.Base):
        name = fields.StringField()
        mix = fields.ListField((str, float))

    person = Person()
    pattern = {"mix": []}
    assert pattern == person.to_struct()

    person.mix.append("something")
    pattern["mix"].append("something")
    assert pattern == person.to_struct()

    person.mix.append(42.0)
    pattern["mix"].append(42.0)
    assert pattern == person.to_struct()

    person.mix.append("different")
    pattern["mix"].append("different")
    assert pattern == person.to_struct()


def test_list_to_struct():
    class Cat(models.Base):
        name = fields.StringField(required=True)
        breed = fields.StringField()

    class Dog(models.Base):
        name = fields.StringField(required=True)
        age = fields.IntField()

    class Person(models.Base):
        name = fields.StringField(required=True)
        surname = fields.StringField(required=True)
        pets = fields.ListField(items_types=[Cat, Dog])

    cat = Cat(name="Garfield")
    dog = Dog(name="Dogmeat", age=9)

    person = Person(name="Johny", surname="Bravo", pets=[cat, dog])
    pattern = {
        "surname": "Bravo",
        "name": "Johny",
        "pets": [{"name": "Garfield"}, {"age": 9, "name": "Dogmeat"}],
    }
    assert pattern == person.to_struct()


def test_to_struct_time():
    class Clock(models.Base):
        time = fields.TimeField()

    clock = Clock()
    clock.time = "12:03:34"

    pattern = {"time": "12:03:34"}
    assert pattern == clock.to_struct()


def test_to_struct_date():
    class Event(models.Base):
        start = fields.DateField()

    event = Event()
    event.start = "2014-04-21"

    pattern = {"start": "2014-04-21"}
    assert pattern == event.to_struct()


def test_to_struct_datetime():
    class Event(models.Base):
        start = fields.DateTimeField()

    event = Event()
    event.start = "2013-05-06 12:03:34"

    pattern = {"start": "2013-05-06T12:03:34"}
    assert pattern == event.to_struct()
