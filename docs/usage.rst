=====
Usage
=====

To use JSON models in a project:

.. code-block:: python

    import jsonmodels

Creating models
---------------

To create models you need to create class that inherits from
:class:`jsonmodels.models.Base` (and *NOT* :class:`jsonmodels.models.PreBase`
to which although refers links in documentation) and have class attributes
which values inherits from :class:`jsonmodels.fields.BaseField` (so all other
fields classes from :mod:`jsonmodels.fields`).

.. code-block:: python

    class Cat(models.Base):

        name = fields.StringField(required=True)
        breed = fields.StringField()
        extra = fields.DictField()


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

Usage
-----

After that you can use it as normal object. You can pass kwargs in constructor
or :meth:`jsonmodels.models.PreBase.populate` method.

.. code-block:: python

    >>> person = Person(name='Chuck')
    >>> person.name
    'Chuck'
    >>> person.surname
    None
    >>> person.populate(surname='Norris')
    >>> person.surname
    'Norris'
    >>> person.name
    'Chuck'

Validation
----------

You can specify which fields are *required*, if required value is absent during
:meth:`jsonmodels.models.PreBase.validate` the
:class:`jsonmodels.error.ValidationError` will be raised.

.. code-block:: python

    >>> bugs = Person(name='Bugs', surname='Bunny')
    >>> bugs.validate()

    >>> dafty = Person()
    >>> dafty.validate()
    *** ValidationError: Field is required!

Note that required fields are not raising error if no value was assigned
during initialization, but first try of accessing will raise it.

.. code-block:: python

    >>> dafty = Person()
    >>> dafty.name
    *** ValidationError: Field is required!

Also validation is made every time new value is assigned, so trying assign
`int` to `StringField` will also raise an error:

.. code-block:: python

    >>> dafty.name = 3
    *** ValidationError: ('Value is wrong, expected type "basestring"', 3)

During casting model to JSON or JSONSchema explicite validation is always
called.

Validators
~~~~~~~~~~

Validators can be passed through `validators` keyword, as a single validator,
or list of validators (so, as you may be expecting, you can't pass object that
extends `List`).

You can try to use validators shipped with this library. To get more details
see :mod:`jsonmodels.validators`. Shipped validators affect generated schema
out of the box, to use full potential JSON schema gives you.

Custom validators
~~~~~~~~~~~~~~~~~

You can always specify your own validators. Custom validator can be object with
`validate` method (which takes precedence) or function (or callable object).

Each validator **must** raise exception to indicate validation
didn't pass. Returning values like `False` won't have any effect.

.. code-block:: python

    >>> class RangeValidator(object):
    ...
    ...   def __init__(self, min, max):
    ...     # Some logic here.
    ...
    ...   def validate(self, value):
    ...     # Some logic here.

    >>> def some_validator(value):
    ...   # Some logic here.

    >>> class Person(models.Base):
    ...
    ...   name = fields.StringField(required=True, validators=some_validator)
    ...   surname = fields.StringField(required=True)
    ...   age = fields.IntField(
    ...     Car, validators=[some_validator, RangeValidator(0, 100)])

If your validator have method `modify_schema` you can use it to affect
generated schema in any way. Given argument is schema for single field. For
example:

.. code-block:: python

    >>> class Length(object):
    ...
    ... def validate(self, value):
    ...     # Some logic here.
    ...
    ... def modify_schema(self, field_schema):
    ...     if self.minimum_value:
    ...         field_schema['minLength'] = self.minimum_value
    ...
    ...     if self.maximum_value:
    ...         field_schema['maxLength'] = self.maximum_value

Default values
--------------

You can specify default value for each of field (and this default value will be
shown in generated schema). Currently only scalars are accepted and model
instances for `EmbeddedField`, like in example below:

.. code-block:: python

    class Pet(models.Base):
        kind = fields.StringField(default="Dog")

    class Person(models.Base):
        name = fields.StringField(default="John Doe")
        age = fields.IntField(default=18)
        pet = fields.EmbeddedField(Pet, default=Pet(kind="Cat"))
        profession = fields.StringField(default=None)

With this schema generated look like this:

.. code-block:: json

    {
        "type": "object",
        "additionalProperties": false,
        "properties": {
            "age": {
                "type": "number",
                "default": 18
            },
        "name": {
                "type": "string",
                "default": "John Doe"
            },
            "pet": {
                "type": "object",
                "additionalProperties": false,
                "properties": {
                    "kind": {
                        "type": "string",
                        "default": "Dog"
                    }
                },
                "default": {
                    "kind": "Cat"
                }
            },
            "profession": {
                "type": "string",
                "default": null
            }
        }
    }

Casting to Python struct (and JSON)
-----------------------------------

Instance of model can be easy casted to Python struct (and thanks to that,
later to JSON). See :meth:`jsonmodels.models.PreBase.to_struct`.

.. code-block:: python

    >>> cat = Cat(name='Garfield')
    >>> dog = Dog(name='Dogmeat', age=9)
    >>> car = Car(registration_number='ASDF 777', color='red')
    >>> person = Person(name='Johny', surname='Bravo', pets=[cat, dog])
    >>> person.car = car
    >>> person.to_struct()
    # (...)

Having Python struct it is easy to cast it to JSON.

.. code-block:: python

    >>> import json
    >>> person_json = json.dumps(person.to_struct())

Creating JSON schema for your model
-----------------------------------

JSON schema, although it is far more friendly than XML schema still have
something in common with its old friend: people don't like to write it and
(probably) they shouldn't do it or even read it. Thanks to `jsonmodels` it
is possible to you to operate just on models.

.. code-block:: python

    >>> person = Person()
    >>> schema = person.to_json_schema()

And thats it! You can serve then this schema through your API or use it for
validation incoming data.

Different names in structure and objects
----------------------------------------

In case you want (or you must) use different names in generated/consumed data
and its schema you can use `name=` param for your fields:

.. code-block:: python

    class Human(models.Base):

        name = fields.StringField()
        surname = fields.StringField(name='second-name')

The `name` value will be usable as `surname` in all places where you are using
**objects** and will be seen as `second-name` in all structures - so in dict
representation and jsonschema.

.. code-block:: python

    >>> john = Human(name='John', surname='Doe')
    >>> john.surname
    'Doe'
    >>> john.to_struct()
    {'name': 'John', 'second-name': 'Doe'}

Remember that your models must not have conflicting names in a way that it
cannot be resolved by model. You can use cross references though, like this:

.. code-block:: python

    class Foo(models.Base):

        one = fields.IntField(name='two')
        two = fields.IntField(name='one')

But remember that **structure name has priority** so with `Foo` model above you
could run into wrong assumptions:

.. code-block:: python

    >>> foo = Foo(one=1, two=2)
    >>> foo.one
    2  # Not 1, like expected
    >>> foo.two
    1  # Not 2, like expected
