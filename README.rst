===========
JSON models
===========

.. image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/
   :alt: Jazzband

.. image:: https://badge.fury.io/py/jsonmodels.svg
   :target: http://badge.fury.io/py/jsonmodels

.. image:: https://github.com/jazzband/jsonmodels/workflows/Test/badge.svg
   :target: https://github.com/jazzband/jsonmodels/actions
   :alt: Tests

.. image:: https://img.shields.io/pypi/dm/jsonmodels.svg
   :target: https://pypi.python.org/pypi/jsonmodels
   :alt: PyPI

.. image:: https://codecov.io/gh/jazzband/jsonmodels/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jazzband/jsonmodels
   :alt: Coverage

`jsonmodels` is library to make it easier for you to deal with structures that
are converted to, or read from JSON.

* Free software: BSD license
* Documentation: http://jsonmodels.rtfd.org
* Source: https://github.com/jazzband/jsonmodels

Features
--------

* Fully tested with Python 3.7+.

* Support for PyPy 3.8 (see implementation notes in docs for more details).

* Create Django-like models:

  .. code-block:: python

    from jsonmodels import models, fields, errors, validators


    class Cat(models.Base):

        name = fields.StringField(required=True)
        breed = fields.StringField()
        love_humans = fields.IntField(nullable=True)


    class Dog(models.Base):

        name = fields.StringField(required=True)
        age = fields.IntField()


    class Car(models.Base):

        registration_number = fields.StringField(required=True)
        engine_capacity = fields.FloatField()
        color = fields.StringField()


    class Person(models.Base):

        name = fields.StringField(required=True)
        surname = fields.StringField(required=True)
        nickname = fields.StringField(nullable=True)
        car = fields.EmbeddedField(Car)
        pets = fields.ListField([Cat, Dog], nullable=True)

* Access to values through attributes:

  .. code-block:: python

    >>> cat = Cat()
    >>> cat.populate(name='Garfield')
    >>> cat.name
    'Garfield'
    >>> cat.breed = 'mongrel'
    >>> cat.breed
    'mongrel'

* Validate models:

  .. code-block:: python

    >>> person = Person(name='Chuck', surname='Norris')
    >>> person.validate()
    None

    >>> dog = Dog()
    >>> dog.validate()
    *** ValidationError: Field "name" is required!

* Cast models to python struct and JSON:

  .. code-block:: python

    >>> cat = Cat(name='Garfield')
    >>> dog = Dog(name='Dogmeat', age=9)
    >>> car = Car(registration_number='ASDF 777', color='red')
    >>> person = Person(name='Johny', surname='Bravo', pets=[cat, dog])
    >>> person.car = car
    >>> person.to_struct()
    {
        'car': {
            'color': 'red',
            'registration_number': 'ASDF 777'
        },
        'surname': 'Bravo',
        'name': 'Johny',
        'nickname': None,
        'pets': [
            {'name': 'Garfield'},
            {'age': 9, 'name': 'Dogmeat'}
        ]
    }

    >>> import json
    >>> person_json = json.dumps(person.to_struct())

* You don't like to write JSON Schema? Let `jsonmodels` do it for you:

  .. code-block:: python

    >>> person = Person()
    >>> person.to_json_schema()
    {
        'additionalProperties': False,
        'required': ['surname', 'name'],
        'type': 'object',
        'properties': {
            'car': {
                'additionalProperties': False,
                'required': ['registration_number'],
                'type': 'object',
                'properties': {
                    'color': {'type': 'string'},
                    'engine_capacity': {'type': ''},
                    'registration_number': {'type': 'string'}
                }
            },
            'surname': {'type': 'string'},
            'name': {'type': 'string'},
            'nickname': {'type': ['string', 'null']}
            'pets': {
                'items': {
                    'oneOf': [
                        {
                            'additionalProperties': False,
                            'required': ['name'],
                            'type': 'object',
                            'properties': {
                                'breed': {'type': 'string'},
                                'name': {'type': 'string'}
                            }
                        },
                        {
                            'additionalProperties': False,
                            'required': ['name'],
                            'type': 'object',
                            'properties': {
                                'age': {'type': 'number'},
                                'name': {'type': 'string'}
                            }
                        },
                        {
                            'type': 'null'
                        }
                    ]
                },
                'type': 'array'
            }
        }
    }

* Validate models and use validators, that affect generated schema:

  .. code-block:: python

    >>> class Person(models.Base):
    ...
    ...     name = fields.StringField(
    ...         required=True,
    ...         validators=[
    ...             validators.Regex('^[A-Za-z]+$'),
    ...             validators.Length(3, 25),
    ...         ],
    ...     )
    ...     age = fields.IntField(
    ...         nullable=True,
    ...         validators=[
    ...             validators.Min(18),
    ...             validators.Max(101),
    ...         ]
    ...     )
    ...     nickname = fields.StringField(
    ...         required=True,
    ...         nullable=True
    ...     )
    ...

    >>> person = Person()
    >>> person.age = 11
    >>> person.validate()
    *** ValidationError: '11' is lower than minimum ('18').
    >>> person.age = None
    >>> person.validate()
    None

    >>> person.age = 19
    >>> person.name = 'Scott_'
    >>> person.validate()
    *** ValidationError: Value "Scott_" did not match pattern "^[A-Za-z]+$".

    >>> person.name = 'Scott'
    >>> person.validate()
    None

    >>> person.nickname = None
    >>> person.validate()
    *** ValidationError: Field is required!

    >>> person.to_json_schema()
    {
        "additionalProperties": false,
        "properties": {
            "age": {
                "maximum": 101,
                "minimum": 18,
                "type": ["number", "null"]
            },
            "name": {
                "maxLength": 25,
                "minLength": 3,
                "pattern": "/^[A-Za-z]+$/",
                "type": "string"
            },
            "nickname": {,
                "type": ["string", "null"]
            }
        },
        "required": [
            "nickname",
            "name"
        ],
        "type": "object"
    }

  You can also validate scalars, when needed:

  .. code-block:: python

    >>> class Person(models.Base):
    ...
    ...     name = fields.StringField(
    ...         required=True,
    ...         validators=[
    ...             validators.Regex('^[A-Za-z]+$'),
    ...             validators.Length(3, 25),
    ...         ],
    ...     )
    ...     age = fields.IntField(
    ...         nullable=True,
    ...         validators=[
    ...             validators.Min(18),
    ...             validators.Max(101),
    ...         ]
    ...     )
    ...     nickname = fields.StringField(
    ...         required=True,
    ...         nullable=True
    ...     )
    ...

    >>> def only_odd_numbers(item):
    ... if item % 2 != 1:
    ...    raise validators.ValidationError("Only odd numbers are accepted")
    ...
    >>> class Person(models.Base):
    ... lucky_numbers = fields.ListField(int, item_validators=[only_odd_numbers])
    ... item_validator_str = fields.ListField(
    ...        str,
    ...        item_validators=[validators.Length(10, 20), validators.Regex(r"\w+")],
    ...        validators=[validators.Length(1, 2)],
    ...    )
    ...
    >>> Person.to_json_schema()
    {
        "type": "object",
        "additionalProperties": false,
        "properties": {
            "item_validator_str": {
                "type": "array",
                "items": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 20,
                    "pattern": "/\\w+/"
                },
                "minItems": 1,
                "maxItems": 2
            },
            "lucky_numbers": {
                "type": "array",
                "items": {
                    "type": "number"
                }
            }
        }
    }

(Note that `only_odd_numbers` did not modify schema, since only class based validators are
able to do that, though it will still work as expected in python. Use class based validators
that can be expressed in json schema if you want to be 100% correct on schema side.)

* Lazy loading, best for circular references:

  .. code-block:: python

    >>> class Primary(models.Base):
    ...
    ...     name = fields.StringField()
    ...     secondary = fields.EmbeddedField('Secondary')

    >>> class Secondary(models.Base):
    ...
    ...    data = fields.IntField()
    ...    first = fields.EmbeddedField('Primary')

  You can use either `Model`, full path `path.to.Model` or relative imports
  `.Model` or `...Model`.

* Using definitions to generate schema for circular references:

  .. code-block:: python

    >>> class File(models.Base):
    ...
    ...     name = fields.StringField()
    ...     size = fields.FloatField()

    >>> class Directory(models.Base):
    ...
    ...     name = fields.StringField()
    ...     children = fields.ListField(['Directory', File])

    >>> class Filesystem(models.Base):
    ...
    ...     name = fields.StringField()
    ...     children = fields.ListField([Directory, File])

    >>> Filesystem.to_json_schema()
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
            "children": {
                "items": {
                    "oneOf": [
                        "#/definitions/directory",
                        "#/definitions/file"
                    ]
                },
                "type": "array"
            }
        },
        "additionalProperties": false,
        "definitions": {
            "directory": {
                "additionalProperties": false,
                "properties": {
                    "children": {
                        "items": {
                            "oneOf": [
                                "#/definitions/directory",
                                "#/definitions/file"
                            ]
                        },
                        "type": "array"
                    },
                    "name": {"type": "string"}
                },
                "type": "object"
            },
            "file": {
                "additionalProperties": false,
                "properties": {
                    "name": {"type": "string"},
                    "size": {"type": "number"}
                },
                "type": "object"
            }
        }
    }

* Dealing with schemaless data

(Plese note that using schemaless fields can cause your models to get out of control - especially if
you are the one responsible for data schema. On the other hand there is usually the case when incomming
data are with no schema defined and schemaless fields are the way to go.)

  .. code-block:: python

    >>> class Event(models.Base):
    ...
    ...     name = fields.StringField()
    ...     size = fields.FloatField()
    ...     extra = fields.DictField()

    >>> Event.to_json_schema()
    {
        "type": "object",
        "additionalProperties": false,
        "properties": {
            "extra": {
                "type": "object"
            },
            "name": {
                "type": "string"
            },
            "size": {
                "type": "float"
            }
        }
    }

`DictField` allow to pass any dict of values (`"type": "object"`), but note, that it will not make any validation
on values except for the dict type.

* Compare JSON schemas:

  .. code-block:: python

    >>> from jsonmodels.utils import compare_schemas
    >>> schema1 = {'type': 'object'}
    >>> schema2 = {'type': 'array'}
    >>> compare_schemas(schema1, schema1)
    True
    >>> compare_schemas(schema1, schema2)
    False

More
----

For more examples and better description see full documentation:
http://jsonmodels.rtfd.org.
