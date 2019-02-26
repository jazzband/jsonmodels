from collections import OrderedDict

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
        empty = fields.MapField(fields.IntField(), fields.StringField())

    model = Model()
    model.str_to_int = {"first": 1, "second": 2}
    model.int_to_str = {1: "first", 2: "second"}

    expected = {
        "str_to_int": {"first": 1, "second": 2},
        "int_to_str": {1: "first", 2: "second"},
    }
    assert expected == model.to_struct()


class CircularMapModel(models.Base):
    """
    Test model used in the following test,
    must be defined outside function for lazy loading
    """
    mapping = fields.MapField(
        fields.IntField(),
        fields.EmbeddedField("CircularMapModel"),
        default=None
    )


def test_map_field_circular():
    model = CircularMapModel(mapping={1: {}, 2: CircularMapModel()})
    expected = {'mapping': {1: {}, 2: {}}}
    assert expected == model.to_struct()


def test_map_field_validation():
    class Model(models.Base):
        str_to_int = fields.MapField(fields.StringField(), fields.IntField())
        int_to_str = fields.MapField(fields.IntField(), fields.StringField(),
                                     required=True)

    assert Model().to_struct() == {"int_to_str": {}}

    with pytest.raises(errors.FieldValidationError):
        Model().str_to_int = {1: "first", 2: "second"}

    with pytest.raises(errors.FieldValidationError):
        Model().int_to_str = {"first": 1, "second": 2}

    model = Model(str_to_int={})
    model.str_to_int[1] = "first"
    with pytest.raises(errors.FieldValidationError):
        model.validate()

    model = Model()
    model.int_to_str["first"] = 1
    with pytest.raises(errors.FieldValidationError):
        model.validate()


def test_generic_field():
    class Model(models.Base):
        field = fields.GenericField()

    model_int = Model(field=1)
    model_str = Model(field="str")
    model_model = Model(field=model_int)
    model_ordered = Model(field=OrderedDict([("b", 2), ("a", 1)]))

    assert {"field": 1} == model_int.to_struct()
    assert {"field": "str"} == model_str.to_struct()
    assert {"field": {"field": 1}} == model_model.to_struct()
    expected = {"field": OrderedDict([("b", 2), ("a", 1)])}
    assert expected == model_ordered.to_struct()


def test_derived_list_omit_empty():

    class Car(models.Base):
        wheels = fields.DerivedListField(fields.StringField(),
                                         omit_empty=True)
        doors = fields.DerivedListField(fields.StringField(),
                                        omit_empty=False)

    viper = Car()
    assert viper.to_struct() == {"doors": []}


def test_automatic_model_detection():

    class FullName(models.Base):
        first_name = fields.StringField()
        last_name = fields.StringField()

    class Car(models.Base):
        models = fields.DerivedListField(fields.StringField(),
                                         omit_empty=False)

    class Person(models.Base):

        names = fields.ListField(
            [str, int, float, bool, FullName, Car],
            help_text='A list of names.',
        )

    person = Person(names=['Daniel', 1, True, {'last_name': 'Schiavini'},
                           {'models': ['Model 3']}])
    assert person.to_struct() == {
        'names': ['Daniel', 1, True, {'last_name': 'Schiavini'},
                  {'models': ['Model 3']}]
    }

    assert isinstance(person.names[-2], FullName)
    assert isinstance(person.names[-1], Car)

    with pytest.raises(errors.FieldValidationError):
        Person(names=[{'last_name': 'Schiavini', 'models': ['Model 3']}])

    with pytest.raises(errors.FieldValidationError):
        Person(names=[{'models': 1}])
