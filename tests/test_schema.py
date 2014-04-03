"""Tests for JSON schema generation."""

import unittest

from jsonmodels import models, fields
from .utils import get_fixture


class TestJsonmodels(unittest.TestCase):

    def test_model1(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField(required=True)
            age = fields.IntField()

        alan = Person()
        schema = alan.to_json_schema()
        pattern = get_fixture('schema1.json')

        self.assertEqual(pattern, schema)
