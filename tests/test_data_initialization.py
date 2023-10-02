import datetime

import pytest

from jsonmodels import errors, fields, models


def test_initialization():
    class Person(models.Base):
        name = fields.StringField()
        surname = fields.StringField()
        age = fields.IntField()
        cash = fields.FloatField()
        extra_data = fields.DictField()

    data = dict(
        name="Alan",
        surname="Wake",
        age=24,
        cash=2445.45,
        extra_data={"location": "Oviedo, Spain", "gender": "Unknown"},
        trash="123qwe",
    )

    alan1 = Person(**data)
    alan2 = Person()
    alan2.populate(**data)
    for alan in [alan1, alan2]:
        assert alan.name == "Alan"
        assert alan.surname == "Wake"
        assert alan.age == 24
        assert alan.cash == 2445.45
        assert alan.extra_data == {"location": "Oviedo, Spain", "gender": "Unknown"}

        assert not hasattr(alan, "trash")


def test_deep_initialization():
    class Car(models.Base):
        brand = fields.StringField()
        extra = fields.DictField()

    class ParkingPlace(models.Base):
        location = fields.StringField()
        car = fields.EmbeddedField(Car)

    data = {
        "location": "somewhere",
        "car": {
            "brand": "awesome brand",
            "extra": {
                "extra_int": 1,
                "extra_str": "a",
                "extra_bool": True,
                "extra_dict": {"I am extra": True},
            },
        },
    }

    parking1 = ParkingPlace(**data)
    parking2 = ParkingPlace()
    parking2.populate(**data)
    for parking in [parking1, parking2]:
        assert parking.location == "somewhere"
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == "awesome brand"
        assert car.extra == {
            "extra_int": 1,
            "extra_str": "a",
            "extra_bool": True,
            "extra_dict": {"I am extra": True},
        }

        assert parking.location == "somewhere"
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == "awesome brand"
        assert car.extra == {
            "extra_int": 1,
            "extra_str": "a",
            "extra_bool": True,
            "extra_dict": {"I am extra": True},
        }


def test_deep_initialization_error_with_multitypes():
    class Viper(models.Base):
        brand = fields.StringField()

    class Lamborghini(models.Base):
        brand = fields.StringField()

    class ParkingPlace(models.Base):
        location = fields.StringField()
        car = fields.EmbeddedField([Viper, Lamborghini])

    data = {"location": "somewhere", "car": {"brand": "awesome brand"}}

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
        "location": "somewhere",
        "cars": [
            {
                "brand": "one",
            },
            {
                "brand": "two",
            },
            {
                "brand": "three",
            },
        ],
    }

    parking1 = Parking(**data)
    parking2 = Parking()
    parking2.populate(**data)
    for parking in [parking1, parking2]:
        assert parking.location == "somewhere"
        cars = parking.cars
        assert isinstance(cars, list)
        assert len(cars) == 3

        values = []
        for car in cars:
            assert isinstance(car, Car)
            values.append(car.brand)
        assert "one" in values
        assert "two" in values
        assert "three" in values


def test_deep_initialization_error_with_list_and_multitypes():
    class Viper(models.Base):
        brand = fields.StringField()

    class Lamborghini(models.Base):
        brand = fields.StringField()

    class Parking(models.Base):
        location = fields.StringField()
        cars = fields.ListField([Viper, Lamborghini])

    data = {
        "location": "somewhere",
        "cars": [
            {
                "brand": "one",
            },
            {
                "brand": "two",
            },
            {
                "brand": "three",
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
        "location": "somewhere",
        "cars": object(),
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

    data = {"names": ["Chuck", "Testa"], "surname": "Norris"}

    person1 = Person(**data)
    person2 = Person()
    person2.populate(**data)

    for person in [person1, person2]:
        assert person.surname == "Norris"
        assert len(person.names) == 2
        assert "Chuck" in person.names
        assert "Testa" in person.names


def test_initialization_with_multi_non_models_types():
    class Person(models.Base):
        name = fields.StringField()
        mix = fields.ListField((str, float))

    data = {"name": "Chuck", "mix": ["something", 42.0, "weird"]}

    person1 = Person(**data)
    person2 = Person()
    person2.populate(**data)

    for person in [person1, person2]:
        assert person.name == "Chuck"
        assert len(person.mix) == 3
        assert "something" in person.mix
        assert 42.0 in person.mix
        assert "weird" in person.mix


def test_initialization_with_wrong_types():
    class Person(models.Base):
        name = fields.StringField()
        mix = fields.ListField((str, float))

    data = {"name": "Chuck", "mix": ["something", 42.0, "weird"]}

    Person(**data)


def test_deep_initialization_for_embed_field():
    class Car(models.Base):
        brand = fields.StringField()

    class ParkingPlace(models.Base):
        location = fields.StringField()
        car = fields.EmbeddedField(Car)

    data = {
        "location": "somewhere",
        "car": Car(brand="awesome brand"),
    }

    parking1 = ParkingPlace(**data)
    parking2 = ParkingPlace()
    parking2.populate(**data)
    for parking in [parking1, parking2]:
        assert parking.location == "somewhere"
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == "awesome brand"

        assert parking.location == "somewhere"
        car = parking.car
        assert isinstance(car, Car)
        assert car.brand == "awesome brand"


def test_int_field_parsing():
    class Counter(models.Base):
        value = fields.IntField()

    counter0 = Counter(value=None)
    assert counter0.value is None
    counter1 = Counter(value=1)
    assert isinstance(counter1.value, int)
    assert counter1.value == 1
    counter2 = Counter(value="2")
    assert isinstance(counter2.value, int)
    assert counter2.value == 2


def test_default_value():
    class Job(models.Base):
        title = fields.StringField()
        company = fields.StringField()

    default_job = Job(tile="Unemployed", company="N/A")
    default_age = 18
    default_name = "John Doe"
    default_height = 1.70
    default_hobbies = ["eating", "reading"]
    default_last_ate = datetime.time()
    default_birthday = datetime.date.today()
    default_time_of_death = datetime.datetime.now()

    class Person(models.Base):
        name = fields.StringField(default=default_name)
        age = fields.IntField(default=default_age)
        height = fields.FloatField(default=default_height)
        job = fields.EmbeddedField(Job, default=default_job)
        hobbies = fields.ListField(items_types=str, default=default_hobbies)
        last_ate = fields.TimeField(default=default_last_ate)
        birthday = fields.DateField(default=default_birthday)
        time_of_death = fields.DateTimeField(default=default_time_of_death)

    p = Person()
    assert p.name == default_name
    assert p.age == default_age
    assert p.height == default_height
    assert p.hobbies == default_hobbies
    assert p.job == default_job
    assert p.last_ate == default_last_ate
    assert p.birthday == default_birthday
    assert p.time_of_death == default_time_of_death
