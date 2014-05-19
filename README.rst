===========
JSON models
===========

.. image:: https://badge.fury.io/py/jsonmodels.png
    :target: http://badge.fury.io/py/jsonmodels

.. image:: https://travis-ci.org/beregond/jsonmodels.png?branch=master
    :target: https://travis-ci.org/beregond/jsonmodels

.. image:: https://pypip.in/d/jsonmodels/badge.png
    :target: https://crate.io/packages/jsonmodels?version=latest


Models to make easier to deal with structures that are to be casted to JSON.

* Free software: BSD license
* Documentation: http://jsonmodels.rtfd.org.

Features
--------

* Fully tested with Python 2.7, 3.4 and PyPy.

* Create Django-like models:

.. code-block:: python

    from jsonmodels import models, fields


    class Cat(models.Base):

        name = fields.StringField(required=True)
        breed = fields.StringField()


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
        car = fields.EmbeddedField(Car)
        pets = fields.ListField([Cat, Dog])

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
                    'engine_capacity': {'type': 'float'},
                    'registration_number': {'type': 'string'}
                }
            },
            'surname': {'type': 'string'},
            'name': {'type': 'string'},
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
                                'age': {'type': 'integer'},
                                'name': {'type': 'string'}
                            }
                        }
                    ]
                },
                'type': 'list'
            }
        }
    }

More
----

For more examples and better description see full documentation:
http://jsonmodels.rtfd.org.
