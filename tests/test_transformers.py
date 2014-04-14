"""Tests for data transformers."""

import unittest
from datetime import datetime

from jsonmodels import models, fields


class _DateField(fields.BaseField):

    _types = (datetime,)


class _DateTransformer(object):

    def transform(self, value):
        return datetime.strptime(value, '%Y-%m-%d')


class TestTransformers(unittest.TestCase):

    def test_transformers(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            birth_date = _DateField(data_transformer=_DateTransformer())

        data = {
            'name': 'Chuck',
            'surname': 'Testa',
            'birth_date': '1990-01-01'
        }

        person = Person(**data)
        person.validate()
        self.assertEqual(person.name, 'Chuck')
        self.assertEqual(person.surname, 'Testa')
        self.assertIsInstance(person.birth_date, datetime)
        self.assertEqual(person.birth_date.year, 1990)
        self.assertEqual(person.birth_date.month, 1)
        self.assertEqual(person.birth_date.day, 1)
