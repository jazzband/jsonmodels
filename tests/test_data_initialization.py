import pytest

from jsonmodels import models, fields, errors


def test_initialization():

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
        assert alan.name == 'Alan'
        assert alan.surname == 'Wake'
        assert alan.age == 24
        assert alan.cash == 2445.45

        assert not hasattr(alan, 'trash')


def test_deep_initialization():

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
        assert parking.location == 'somewhere'
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == 'awesome brand'

        assert parking.location == 'somewhere'
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == 'awesome brand'


def test_deep_initialization_error_with_multitypes():

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

    with pytest.raises(errors.ValidationError):
        ParkingPlace(**data)

    place = ParkingPlace()
    with pytest.raises(errors.ValidationError):
        place.populate(**data)


def test_deep_initialization_with_list():

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
        assert parking.location == 'somewhere'
        cars = parking.cars
        assert isinstance(cars, list)
        assert len(cars) == 3

        values = []
        for car in cars:
            assert isinstance(car, Car)
            values.append(car.brand)
        assert 'one' in values
        assert 'two' in values
        assert 'three' in values


def test_deep_initialization_error_with_list_and_multitypes():

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

    with pytest.raises(errors.ValidationError):
        Parking(**data)

    parking = Parking()
    with pytest.raises(errors.ValidationError):
        parking.populate(**data)


def test_deep_initialization_error_when_result_non_iterable():

    class Viper(models.Base):

        brand = fields.StringField()

    class Lamborghini(models.Base):

        brand = fields.StringField()

    class Parking(models.Base):

        location = fields.StringField()
        cars = fields.ListField([Viper, Lamborghini])

    data = {
        'location': 'somewhere',
        'cars': object(),
    }

    with pytest.raises(errors.ValidationError):
        Parking(**data)

    parking = Parking()
    with pytest.raises(errors.ValidationError):
        parking.populate(**data)


def test_initialization_with_non_models_types():

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
        assert person.surname == 'Norris'
        assert len(person.names) == 2
        assert 'Chuck' in person.names
        assert 'Testa' in person.names


def test_initialization_with_multi_non_models_types():

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
        assert person.name == 'Chuck'
        assert len(person.mix) == 3
        assert 'something' in person.mix
        assert 42.0 in person.mix
        assert 'weird' in person.mix


def test_initialization_with_wrong_types():

    class Person(models.Base):

        name = fields.StringField()
        mix = fields.ListField((str, float))

    data = {
        'name': 'Chuck',
        'mix': ['something', 42.0, 'weird']
    }

    Person(**data)


def test_deep_initialization_for_embed_field():

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
        assert parking.location == 'somewhere'
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == 'awesome brand'

        assert parking.location == 'somewhere'
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == 'awesome brand'
