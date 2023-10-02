import pytest

from jsonmodels import errors, fields, models


def test_model1():
    class Person(models.Base):
        name = fields.StringField()
        surname = fields.StringField()
        age = fields.IntField()
        extra = fields.DictField()

    alan = Person()

    alan.name = "Alan"
    alan.surname = "Wake"
    alan.age = 34
    alan.extra = {"extra_value": 1}


def test_required():
    class Person(models.Base):
        name = fields.StringField(required=True)
        surname = fields.StringField()
        age = fields.IntField()

    alan = Person()
    with pytest.raises(errors.ValidationError):
        alan.validate()

    alan.name = "Chuck"
    alan.validate()


def test_type_validation():
    class Person(models.Base):
        name = fields.StringField()
        age = fields.IntField()

    alan = Person()

    alan.age = 42


def test_base_field_should_not_be_usable():
    class Person(models.Base):
        name = fields.BaseField()

    alan = Person()

    with pytest.raises(errors.ValidationError):
        alan.name = "some name"

    with pytest.raises(errors.ValidationError):
        alan.name = 2345


def test_value_replacements():
    class Person(models.Base):
        name = fields.StringField()
        age = fields.IntField()
        cash = fields.FloatField()
        children = fields.ListField()

    alan = Person()
    assert alan.name is None
    assert alan.age is None
    assert alan.cash is None
    assert isinstance(alan.children, list)


def test_list_field():
    class Car(models.Base):
        wheels = fields.ListField()

    viper = Car()

    viper.wheels.append("some")
    viper.wheels.append("not necessarily")
    viper.wheels.append("proper")
    viper.wheels.append("wheels")


def test_list_field_types():
    class Wheel(models.Base):
        pass

    class Wheel2(models.Base):
        pass

    class Car(models.Base):
        wheels = fields.ListField(items_types=[Wheel])

    viper = Car()

    viper.wheels.append(Wheel())
    viper.wheels.append(Wheel())

    with pytest.raises(errors.ValidationError):
        viper.wheels.append(Wheel2)


def test_list_field_types_when_assigning():
    class Wheel(models.Base):
        pass

    class Wheel2(models.Base):
        pass

    class Car(models.Base):
        wheels = fields.ListField(items_types=[Wheel])

    viper = Car()

    viper.wheels.append(Wheel())
    viper.wheels[0] = Wheel()

    with pytest.raises(errors.ValidationError):
        viper.wheels[1] = Wheel2


def test_list_field_for_subtypes():
    class Car(models.Base):
        pass

    class Viper(Car):
        pass

    class Lamborghini(Car):
        pass

    class Garage1(models.Base):
        cars = fields.ListField(items_types=[Car])

    garage = Garage1()
    garage.cars.append(Car())
    garage.cars.append(Viper())
    garage.cars.append(Lamborghini())

    class Garage2(models.Base):
        cars = fields.ListField(items_types=[Viper, Lamborghini])

    garage = Garage2()
    garage.cars.append(Viper())
    garage.cars.append(Lamborghini())

    with pytest.raises(errors.ValidationError):
        garage.cars.append(Car())


def test_list_validation():
    class Garage(models.Base):
        cars = fields.ListField()

    garage = Garage()

    with pytest.raises(errors.ValidationError):
        garage.cars = "some string"


def test_embedded_model():
    class Secondary(models.Base):
        data = fields.IntField()

    class Primary(models.Base):
        name = fields.StringField()
        secondary = fields.EmbeddedField(Secondary)

    entity = Primary()
    assert entity.secondary is None
    entity.name = "chuck"
    entity.secondary = Secondary()
    entity.secondary.data = 42

    with pytest.raises(errors.ValidationError):
        entity.secondary = "something different"

    entity.secondary = None


def test_embedded_required_validation():
    class Secondary(models.Base):
        data = fields.IntField(required=True)

    class Primary(models.Base):
        name = fields.StringField()
        secondary = fields.EmbeddedField(Secondary)

    entity = Primary()
    sec = Secondary()
    sec.data = 33
    entity.secondary = sec

    with pytest.raises(errors.ValidationError):
        entity.secondary.data = None

    entity.secondary = None

    class Primary(models.Base):
        name = fields.StringField()
        secondary = fields.EmbeddedField(Secondary, required=True)

    entity = Primary()
    sec = Secondary()
    sec.data = 33
    entity.secondary = sec

    with pytest.raises(errors.ValidationError):
        entity.secondary.data = None


def test_embedded_inheritance():
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
    place.car = Lamborghini()

    with pytest.raises(errors.ValidationError):
        place.car = Car()

    class ParkingPlace(models.Base):
        location = fields.StringField()
        car = fields.EmbeddedField(Car)

    place = ParkingPlace()

    place.car = Viper()
    place.car = Lamborghini()
    place.car = Car()


def test_iterable():
    class Person(models.Base):
        name = fields.StringField()
        surname = fields.StringField()
        age = fields.IntField()
        cash = fields.FloatField()

    alan = Person()

    alan.name = "Alan"
    alan.surname = "Wake"
    alan.age = 24
    alan.cash = 2445.45

    pattern = {
        "name": "Alan",
        "surname": "Wake",
        "age": 24,
        "cash": 2445.45,
    }

    result = {}
    for name, field in alan:
        result[name] = field.__get__(alan)

    assert pattern == result


def test_get_field():
    name_field = fields.StringField()
    surname_field = fields.StringField()
    age_field = fields.IntField()

    class Person(models.Base):
        name = name_field
        surname = surname_field
        age = age_field

    alan = Person()

    assert alan.get_field("name") is name_field
    assert alan.get_field("surname") is surname_field
    assert alan.get_field("age") is age_field


def test_repr():
    class Person(models.Base):
        name = fields.StringField()
        surname = fields.StringField()
        age = fields.IntField()

    chuck = Person()

    assert chuck.__repr__() == "Person()"
    assert chuck.__str__() == "Person object"

    class Person2(models.Base):
        name = fields.StringField()
        surname = fields.StringField()
        age = fields.IntField()

        def __str__(self):
            return self.name

    chuck = Person2()

    assert chuck.__repr__() == "Person2()"

    chuck.name = "Chuck"
    assert chuck.__repr__() == "Person2(name='Chuck')"
    assert chuck.__str__() == "Chuck"

    chuck.name = "Testa"
    chuck.age = 42
    assert chuck.__repr__() == "Person2(age=42, name='Testa')"
    assert chuck.__str__() == "Testa"


def test_list_field_with_non_model_types():
    class Person(models.Base):
        names = fields.ListField(str)
        surname = fields.StringField()

    person = Person(surname="Norris")
    person.names.append("Chuck")
    person.names.append("Testa")


def test_help_text():
    class Person(models.Base):
        name = fields.StringField(help_text="Name of person.")
        age = fields.IntField(help_text="Age of person.")

    person = Person()
    assert person.get_field("name").help_text == "Name of person."
    assert person.get_field("age").help_text == "Age of person."


def test_types():
    class Person:
        pass

    class Person2:
        pass

    allowed_types = (Person,)

    field = fields.EmbeddedField(allowed_types)
    assert allowed_types == field.types

    allowed_types = (Person, Person2)

    field = fields.EmbeddedField(allowed_types)
    assert allowed_types == field.types


def test_items_types():
    class Person:
        pass

    class Person2:
        pass

    allowed_types = (Person,)

    field = fields.ListField(allowed_types)
    assert allowed_types == field.items_types

    allowed_types = (Person, Person2)

    field = fields.ListField(allowed_types)
    assert allowed_types == field.items_types

    field = fields.ListField()
    assert tuple() == field.items_types


def test_required_embedded_field():
    class Secondary(models.Base):
        data = fields.IntField()

    class Primary(models.Base):
        name = fields.StringField()
        secondary = fields.EmbeddedField(Secondary, required=True)

    entity = Primary()
    with pytest.raises(errors.ValidationError):
        entity.validate()
    entity.secondary = Secondary()
    entity.validate()

    class Primary(models.Base):
        name = fields.StringField()
        secondary = fields.EmbeddedField(Secondary, required=False)

    entity = Primary()
    entity.validate()

    entity.secondary = None
    entity.validate()


def test_assignation_of_list_of_models():
    class Wheel(models.Base):
        pass

    class Car(models.Base):
        wheels = fields.ListField(items_types=[Wheel])

    viper = Car()
    viper.wheels = None
    viper.wheels = [Wheel()]


def test_equality_of_different_types():
    class A(models.Base):
        pass

    class B(A):
        pass

    class C(models.Base):
        pass

    assert A() == A()
    assert A() != B()
    assert B() != A()
    assert A() != C()


def test_equality_of_simple_models():
    class Person(models.Base):
        name = fields.StringField()
        age = fields.IntField()

    p1 = Person(name="Jack")
    p2 = Person(name="Jack")

    assert p1 == p2
    assert p2 == p1

    p3 = Person(name="Jack", age=100)
    assert p1 != p3
    assert p3 != p1

    p4 = Person(name="Jill")
    assert p1 != p4
    assert p4 != p1


def test_equality_embedded_objects():
    class Person(models.Base):
        name = fields.StringField()

    class Company(models.Base):
        chairman = fields.EmbeddedField(Person)

    c1 = Company(chairman=Person(name="Pete"))
    c2 = Company(chairman=Person(name="Pete"))

    assert c1 == c2
    assert c2 == c1

    c3 = Company(chairman=Person(name="Joshua"))

    assert c1 != c3
    assert c3 != c1


def test_equality_list_fields():
    class Wheel(models.Base):
        pressure = fields.FloatField()

    class Car(models.Base):
        wheels = fields.ListField(items_types=[Wheel])

    car = Car(
        wheels=[
            Wheel(pressure=1),
            Wheel(pressure=2),
            Wheel(pressure=3),
            Wheel(pressure=4),
        ],
    )

    another_car = Car(
        wheels=[
            Wheel(pressure=1),
            Wheel(pressure=2),
            Wheel(pressure=3),
            Wheel(pressure=4),
        ],
    )

    assert car == another_car

    different_car = Car(
        wheels=[
            Wheel(pressure=4),
            Wheel(pressure=3),
            Wheel(pressure=2),
            Wheel(pressure=1),
        ],
    )
    assert car != different_car


def test_equality_missing_required_field():
    class Model(models.Base):
        name = fields.StringField(required=True)
        age = fields.IntField()

    assert Model(age=1) == Model(age=1)
    assert Model(age=1) != Model(age=2)
    assert Model(name="William", age=1) != Model(age=1)
