#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jsonmodels
----------------------------------

Tests for `jsonmodels` module.
"""

import unittest

from jsonmodels import models, fields, error


class TestJsonmodels(unittest.TestCase):

    def test_model1(self):

        class Person(models.Base):

            name = fields.StringField()
            surname = fields.StringField()
            age = fields.IntField()

        alan = Person()
        alan.validate()

        alan.name = 'Alan'
        alan.surname = 'Wake'
        alan.age = 34
        alan.validate()

    def test_required(self):

        class Person(models.Base):

            name = fields.StringField(required=True)
            surname = fields.StringField()
            age = fields.IntField()

        alan = Person()
        self.assertRaises(error.ValidationError, alan.validate)

        alan.name = 'Chuck'
        alan.validate()

if __name__ == '__main__':
    unittest.main()
