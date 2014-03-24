"""Tests for JSON schema generation."""

import unittest

from jsonmodels import models, fields, error


class TestJsonmodels(unittest.TestCase):

    def test_model1(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()

        alan = Person()
        schema = alan.to_json_schema()

        pattern = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'surname': {'type': 'string'},
                'age': {'type': 'integer'},
            },
            'additionalProperties': False,
        }

        self.assertEqual(pattern, schema)
