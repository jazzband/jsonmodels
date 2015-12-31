====================
Implementation notes
====================

Below you can read some implementation specific quirks you should know/remember
about when you are using `jsonmodels` (especially on production
servers/applications).

PyPy
----

PyPy is supported, although there is one problem with garbage collecting:
**PyPy's weakref implementation is not stable, so garbage collecting may not
work, which may cause memory leak** (values for nonexistent objects may still
be preserved, since descriptors are for fields implementation).

All others features are fully supported.
