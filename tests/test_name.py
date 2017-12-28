import pytest

from jsonmodels import models, fields


def test_fields_can_have_different_names():

    class Human(models.Base):

        name = fields.StringField()
        surname = fields.StringField(name='second-name')

    chuck = Human(name='Chuck', surname='Testa')
    assert chuck.to_struct() == {'name': 'Chuck', 'second-name': 'Testa'}


def test_only_subset_of_names_is_accepted():
    with pytest.raises(ValueError):
        fields.StringField(name='totally wrong name')
    with pytest.raises(ValueError):
        fields.StringField(name='wrong!')
    with pytest.raises(ValueError):
        fields.StringField(name='~wrong')


def test_load_data_from_structure_names():

    class Human(models.Base):

        name = fields.StringField()
        surname = fields.StringField(name='second-name')

    data = {'name': 'Chuck', 'second-name': 'Testa'}
    chuck = Human(**data)
    assert chuck.name == 'Chuck'
    assert chuck.surname == 'Testa'

    data = {'name': 'Chuck', 'surname': 'Testa'}
    chuck = Human(**data)
    assert chuck.name == 'Chuck'
    assert chuck.surname == 'Testa'


def test_names_duplicates_are_invalid():

    with pytest.raises(ValueError):
        class Human(models.Base):
            name = fields.StringField(name='surname')
            surname = fields.StringField()

    class OtherHuman(models.Base):
        name = fields.StringField(name='surname')
        surname = fields.StringField(name='name')
