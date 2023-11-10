import pytest

from jsonmodels import fields, models


def test_fields_can_have_different_names():
    class Human(models.Base):
        name = fields.StringField()
        surname = fields.StringField(name="second-name")

    chuck = Human(name="Chuck", surname="Testa")
    assert chuck.to_struct() == {"name": "Chuck", "second-name": "Testa"}


def test_only_subset_of_names_is_accepted():
    with pytest.raises(ValueError):
        fields.StringField(name="totally wrong name")
    with pytest.raises(ValueError):
        fields.StringField(name="wrong!")
    with pytest.raises(ValueError):
        fields.StringField(name="~wrong")


def test_load_data_from_structure_names():
    class Human(models.Base):
        name = fields.StringField()
        surname = fields.StringField(name="second-name")

    data = {"name": "Chuck", "second-name": "Testa"}
    chuck = Human(**data)
    assert chuck.name == "Chuck"
    assert chuck.surname == "Testa"

    data = {"name": "Chuck", "surname": "Testa"}
    chuck = Human(**data)
    assert chuck.name == "Chuck"
    assert chuck.surname == "Testa"


def test_names_duplicates_are_invalid():
    with pytest.raises(ValueError):

        class Human(models.Base):
            name = fields.StringField(name="surname")
            surname = fields.StringField()

    class OtherHuman(models.Base):
        name = fields.StringField(name="surname")
        surname = fields.StringField(name="name")


def test_data_assignation():
    """If names collide - value may be assigned twice.

    If we pass value for `brand` - the value whould be assigned only to
    `description` field (as this is its structure name). In case you pass
    two values - for description AND brand - only structure name is taken into
    account.

    This is done so models can be 'smart' - to use structure name by default,
    but take attribute names as fallback, so it won't mess with more convinient
    workflow.
    """

    class Product(models.Base):
        brand = fields.StringField(name="description")
        description = fields.StringField(name="product_description")

    product = Product(description="foo")
    assert product.brand == "foo"
    assert product.description is None


def test_nested_data():
    class Pet(models.Base):
        name = fields.StringField(required=True, name="pets_name")
        age = fields.IntField()

    class Human(models.Base):
        name = fields.StringField()
        pet = fields.EmbeddedField(Pet, name="owned-pet")

    data = {"name": "John", "owned-pet": {"pets_name": "Pinky", "age": 2}}
    human = Human(**data)
    assert human.pet.name == "Pinky"


def test_cross_names():
    class Foo(models.Base):
        one = fields.IntField(name="two")
        two = fields.IntField(name="one")

    foo = Foo(one=1, two=2)
    assert foo.one == 2
    assert foo.two == 1
