import pytest
from jsonmodels import models, fields, validators, errors


def test_deprecated_structue_name():
    field = fields.BoolField(name='field')
    assert field.structue_name('default') == 'field'

    field = fields.BoolField()
    assert field.structue_name('default') == 'default'


def test_bool_field():

    field = fields.BoolField()

    class Person(models.Base):

        is_programmer = field

    person = Person()
    assert person.is_programmer is None

    person.is_programmer = True
    assert person.is_programmer is True

    person.is_programmer = False
    assert person.is_programmer is False

    assert field.parse_value(True) is True
    assert field.parse_value('something') is True
    assert field.parse_value(object()) is True

    assert field.parse_value(None) is None

    assert field.parse_value(False) is False
    assert field.parse_value(0) is False
    assert field.parse_value('') is False
    assert field.parse_value([]) is False


def test_custom_field():
    class NameField(fields.StringField):
        def __init__(self):
            super(NameField, self).__init__(required=True)

    class Person(models.Base):
        name = NameField()
        surnames = fields.DerivedListField(NameField())

    person = Person(name='Person')
    person.surnames = ['Surname', 'Surname']

    expected = {'name': 'Person', 'surnames': ['Surname', 'Surname']}
    assert person.to_struct() == expected


def test_custom_field_validation():
    class NameField(fields.StringField):
        def __init__(self):
            super(NameField, self).__init__(
                required=True,
                validators=validators.Regex("[A-Z][a-z]+")
            )

    class Person(models.Base):
        name = NameField()
        surnames = fields.DerivedListField(NameField())

    with pytest.raises(errors.FieldValidationError):
        Person(name=None)

    with pytest.raises(errors.FieldValidationError):
        Person().name = "N"

    with pytest.raises(errors.FieldValidationError):
        Person(surnames=[None])

    person = Person()
    person.surnames.append(None)
    with pytest.raises(errors.FieldValidationError):
        person.validate()


def test_map_field():
    class Model(models.Base):
        str_to_int = fields.MapField(fields.StringField(), fields.IntField())
        int_to_str = fields.MapField(fields.IntField(), fields.StringField())

    model = Model()
    model.str_to_int = {"first": 1, "second": 2}
    model.int_to_str = {1: "first", 2: "second"}

    expected = {
        "str_to_int": {"first": 1, "second": 2},
        "int_to_str": {1: "first", 2: "second"},
    }
    assert expected == model.to_struct()


def test_map_field_validation():
    class Model(models.Base):
        str_to_int = fields.MapField(fields.StringField(), fields.IntField())
        int_to_str = fields.MapField(fields.IntField(), fields.StringField())

    with pytest.raises(errors.FieldValidationError):
        Model().str_to_int = {1: "first", 2: "second"}

    with pytest.raises(errors.FieldValidationError):
        Model().int_to_str = {"first": 1, "second": 2}

    model = Model()
    model.str_to_int[1] = "first"
    with pytest.raises(errors.FieldValidationError):
        model.validate()

    model = Model()
    model.int_to_str["first"] = 1
    with pytest.raises(errors.FieldValidationError):
        model.validate()


def test_any_field():
    class Model(models.Base):
        field = fields.AnyField()

    assert {"field": 1} == Model(field=1).to_struct()
    assert {"field": "1"} == Model(field="1").to_struct()
    assert {"field": {"field": {}}} == Model(field=Model(field={})).to_struct()
