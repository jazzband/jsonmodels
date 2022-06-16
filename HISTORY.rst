.. :changelog:

History
-------

2.5.1 (2022-06-16)
++++++++++++++++++

* Specified PyPy version to PyPy 3.8.
* Added support for Python 3.10.

2.5.0 (2021-07-26)
++++++++++++++++++

* Improvied error messages for field validation errors.
* Allowed to validate non model list items.
* Added DictField.

2.4.1 (2021-02-19)
++++++++++++++++++

* Added Python 3.8 and 3.9 support.
* Removed Python 2.7, 3.3 and 3.5 support.

2.4 (2018-12-01)
++++++++++++++++

* Fixed length validator.
* Added Python 3.7 support.

2.3 (2018-02-04)
++++++++++++++++

* Added name mapping for fields.
* Added value parsing to IntField.
* Fixed bug with ECMA regex flags recognition.

2.2 (2017-08-21)
++++++++++++++++

* Fixed time fields, when value is not required.
* Dropped support for python 2.6
* Added support for python 3.6
* Added nullable param for fields.
* Improved model representation.

2.1.5 (2017-02-01)
++++++++++++++++++

* Fixed DateTimefield error when value is None.
* Fixed comparing models without required values.

2.1.4 (2017-01-24)
++++++++++++++++++

* Allow to compare models based on their type and fields (rather than their
  reference).

2.1.3 (2017-01-16)
++++++++++++++++++

* Fixed generated schema.
* Improved JSON serialization.

2.1.2 (2016-01-06)
++++++++++++++++++

* Fixed memory leak.

2.1.1 (2015-11-15)
++++++++++++++++++

* Added support for Python 2.6, 3.2 and 3.5.

2.1 (2015-11-02)
++++++++++++++++

* Added lazy loading of types.
* Added schema generation for circular models.
* Improved readability of validation error.
* Fixed structure generation for list field.

2.0.1 (2014-11-15)
++++++++++++++++++

* Fixed schema generation for primitives.

2.0 (2014-11-14)
++++++++++++++++

* Fields now are descriptors.
* Empty required fields are still validated only during explicite validations.

Backward compatibility breaks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Renamed _types to types in fields.
* Renamed _items_types to items_types in ListField.
* Removed data transformers.
* Renamed module `error` to `errors`.
* Removed explicit validation - validation occurs at assign time.
* Renamed `get_value_replacement` to `get_default_value`.
* Renamed modules `utils` to `utilities`.

1.4 (2014-07-22)
++++++++++++++++

* Allowed validators to modify generated schema.
* Added validator for maximum value.
* Added utilities to convert regular expressions between Python and ECMA
  formats.
* Added validator for regex.
* Added validator for minimum value.
* By default "validators" property of field is an empty list.

1.3.1 (2014-07-13)
++++++++++++++++++

* Fixed generation of schema for BoolField.

1.3 (2014-07-13)
++++++++++++++++

* Added new fields (BoolField, TimeField, DateField and DateTimeField).
* ListField is always not required.
* Schema can be now generated from class itself (not from an instance).

1.2 (2014-06-18)
++++++++++++++++

* Fixed values population, when value is not dictionary.
* Added custom validators.
* Added tool for schema comparison.

1.1.1 (2014-06-07)
++++++++++++++++++

* Added possibility to populate already initialized data to EmbeddedField.
* Added `compare_schemas` utility.

1.1 (2014-05-19)
++++++++++++++++

* Added docs.
* Added json schema generation.
* Added tests for PEP8 and complexity.
* Moved to Python 3.4.
* Added PEP257 compatibility.
* Added help text to fields.

1.0.5 (2014-04-14)
++++++++++++++++++

* Added data transformers.

1.0.4 (2014-04-13)
++++++++++++++++++

* List field now supports simple types.

1.0.3 (2014-04-10)
++++++++++++++++++

* Fixed compatibility with Python 3.
* Fixed `str` and `repr` methods.

1.0.2 (2014-04-03)
++++++++++++++++++

* Added deep data initialization.

1.0.1 (2014-04-03)
++++++++++++++++++

* Added `populate` method.

1.0 (2014-04-02)
++++++++++++++++

* First stable release on PyPI.

0.1.0 (2014-03-17)
++++++++++++++++++

* First release on PyPI.
