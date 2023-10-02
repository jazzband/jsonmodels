"""Test for validators."""

import pytest

from jsonmodels import errors, fields, models, validators


class FakeValidator:
    def __init__(self):
        self.called_with = None
        self.called_amount = 0

    def validate(self, value):
        self.called_amount = self.called_amount + 1
        self.called_with = value

    def assert_called_once_with(self, value):
        if value != self.called_with or self.called_amount != 1:
            raise AssertionError('Assert called once with "{}" failed!')


def test_validation():
    validator1 = FakeValidator()
    validator2 = FakeValidator()

    called = []
    arg = []

    def validator3(value):
        called.append(1)
        arg.append(value)

    class Person(models.Base):
        name = fields.StringField(required=True, validators=[validator1, validator2])
        surname = fields.StringField(required=True)
        age = fields.IntField(validators=validator3)
        cash = fields.FloatField()

    person = Person()
    person.name = "John"
    person.surname = "Smith"
    person.age = 33
    person.cash = 123567.89

    validator1.assert_called_once_with("John")
    validator2.assert_called_once_with("John")

    assert 1 == sum(called)
    assert 33 == arg.pop()


def test_validators_are_always_iterable():
    class Person(models.Base):
        children = fields.ListField()

    alan = Person()

    assert isinstance(alan.get_field("children").validators, list)


def test_get_field_not_found():
    class Person(models.Base):
        children = fields.ListField()

    alan = Person()

    with pytest.raises(errors.FieldNotFound):
        alan.get_field("bazinga")


def test_min_validation():
    validator = validators.Min(3)
    assert 3 == validator.minimum_value

    validator.validate(4)
    validator.validate(3)

    with pytest.raises(errors.ValidationError):
        validator.validate(2)
    with pytest.raises(errors.ValidationError):
        validator.validate(-2)


def test_exclusive_validation():
    validator = validators.Min(3, True)
    assert 3 == validator.minimum_value

    validator.validate(4)
    with pytest.raises(errors.ValidationError):
        validator.validate(3)
    with pytest.raises(errors.ValidationError):
        validator.validate(2)
    with pytest.raises(errors.ValidationError):
        validator.validate(-2)


def test_max_validation():
    validator = validators.Max(42)
    assert 42 == validator.maximum_value

    validator.validate(4)
    validator.validate(42)
    with pytest.raises(errors.ValidationError):
        validator.validate(42.01)
    with pytest.raises(errors.ValidationError):
        validator.validate(43)


def test_max_exclusive_validation():
    validator = validators.Max(42, True)
    assert 42 == validator.maximum_value

    validator.validate(4)
    with pytest.raises(errors.ValidationError):
        validator.validate(42)
    with pytest.raises(errors.ValidationError):
        validator.validate(42.01)
    with pytest.raises(errors.ValidationError):
        validator.validate(43)


def test_regex_validation():
    validator = validators.Regex("some")
    assert "some" == validator.pattern

    validator.validate("some string")
    validator.validate("get some chips")
    with pytest.raises(errors.ValidationError):
        validator.validate("asdf")
    with pytest.raises(errors.ValidationError):
        validator.validate("trololo")


def test_regex_validation_flags():
    # Invalid flags ignored
    validator = validators.Regex("foo", bla=True, ble=False, ignorecase=True)
    assert validator.flags == [validators.Regex.FLAGS["ignorecase"]]

    # Flag kwargs must be True-y
    validator = validators.Regex("foo", ignorecase=False, multiline=True)
    assert validator.flags == [validators.Regex.FLAGS["multiline"]]

    # ECMA pattern flags recognized
    validator = validators.Regex("/foo/im")
    assert sorted(validator.flags) == sorted(
        [
            validators.Regex.FLAGS["multiline"],
            validators.Regex.FLAGS["ignorecase"],
        ]
    )

    # ECMA pattern overrides flags kwargs
    validator = validators.Regex("/foo/", ignorecase=True, multiline=True)
    assert validator.flags == []


def test_regex_validation_for_wrong_type():
    validator = validators.Regex("some")
    assert "some" == validator.pattern

    with pytest.raises(errors.ValidationError):
        validator.validate(1)


def test_validation_2():
    validator = validators.Regex("^some[0-9]$")
    assert "^some[0-9]$" == validator.pattern

    validator.validate("some0")
    with pytest.raises(errors.ValidationError):
        validator.validate("some")
    with pytest.raises(errors.ValidationError):
        validator.validate(" some")
    with pytest.raises(errors.ValidationError):
        validator.validate("asdf")
    with pytest.raises(errors.ValidationError):
        validator.validate("trololo")


def test_validation_ignorecase():
    validator = validators.Regex("^some$")
    validator.validate("some")
    with pytest.raises(errors.ValidationError):
        validator.validate("sOmE")

    validator = validators.Regex("^some$", ignorecase=True)
    validator.validate("some")
    validator.validate("SoMe")


def test_validation_multiline():
    validator = validators.Regex("^s.*e$")
    validator.validate("some")
    with pytest.raises(errors.ValidationError):
        validator.validate("some\nso more")

    validator = validators.Regex("^s.*e$", multiline=True)
    validator.validate("some")
    validator.validate("some\nso more")


def test_regex_validator():
    class Person(models.Base):
        name = fields.StringField(
            validators=validators.Regex("^[a-z]+$", ignorecase=True)
        )

    person = Person()

    with pytest.raises(errors.ValidationError):
        person.name = "123"

    person.name = "Jimmy"


def test_regex_validator_when_ecma_regex_given():
    class Person(models.Base):
        name = fields.StringField(
            validators=validators.Regex("/^[a-z]+$/i", ignorecase=False)
        )

    person = Person()

    with pytest.raises(errors.ValidationError):
        person.name = "123"

    person.name = "Jimmy"


def test_init():
    validator = validators.Length(0, 10)
    assert 0 == validator.minimum_value
    assert 10 == validator.maximum_value

    validator = validators.Length(0)
    assert 0 == validator.minimum_value
    assert validator.maximum_value is None

    validator = validators.Length(maximum_value=10)
    assert 10 == validator.maximum_value
    assert validator.minimum_value is None

    with pytest.raises(ValueError):
        validators.Length()


def test_length_validation_string_min_max():
    validator = validators.Length(1, 10)
    validator.validate("word")
    validator.validate("w" * 10)
    validator.validate("w")

    with pytest.raises(errors.ValidationError):
        validator.validate("")
    with pytest.raises(errors.ValidationError):
        validator.validate("na" * 10)


def test_length_validation_string_min():
    validator = validators.Length(minimum_value=1)
    validator.validate("a")
    validator.validate("aasdasd" * 1000)
    with pytest.raises(errors.ValidationError):
        validator.validate("")


def test_length_validation_string_max():
    validator = validators.Length(maximum_value=10)
    validator.validate("")
    validator.validate("a")
    validator.validate("a" * 10)
    with pytest.raises(errors.ValidationError):
        validator.validate("a" * 11)


def test_length_validation_list_min_max():
    validator = validators.Length(1, 10)
    validator.validate([1, 2, 3, 4])
    validator.validate([1] * 10)
    validator.validate([1])

    with pytest.raises(errors.ValidationError):
        validator.validate([])
    with pytest.raises(errors.ValidationError):
        validator.validate([1, 2] * 10)


def test_length_validation_list_min():
    validator = validators.Length(minimum_value=1)
    validator.validate([1])
    validator.validate(range(1000))
    with pytest.raises(errors.ValidationError):
        validator.validate([])


def test_length_validation_list_max():
    validator = validators.Length(maximum_value=10)
    validator.validate([])
    validator.validate([1])
    validator.validate([1] * 10)
    with pytest.raises(errors.ValidationError):
        validator.validate([1] * 11)


def test_validation_nullable():
    class Emb(models.Base):
        name = fields.StringField(nullable=True)

    class User(models.Base):
        name = fields.StringField(nullable=True)
        props = fields.ListField([str, int, float], nullable=True)
        embedded = fields.EmbeddedField(Emb, nullable=True)

    user = User(name=None, props=None)
    user.validate()


def test_enum_validation():
    validator = validators.Enum("cat", "dog", "fish")

    validator.validate("cat")
    validator.validate("dog")
    validator.validate("fish")

    with pytest.raises(errors.ValidationError):
        validator.validate("horse")
