import six

from . import parsers, errors
from .fields import BaseField
from .errors import ValidationError


class JsonmodelMeta(type):

    def __new__(cls, name, bases, attributes):
        cls.validate_fields(attributes)
        return super(cls, cls).__new__(cls, name, bases, attributes)

    @staticmethod
    def validate_fields(attributes):
        fields = {
            key: value for key, value in attributes.items()
            if isinstance(value, BaseField)
        }
        taken_names = set()
        for name, field in fields.items():
            structure_name = field.structure_name(name)
            if structure_name in taken_names:
                raise ValueError('Name taken', structure_name, name)
            taken_names.add(structure_name)


class Base(six.with_metaclass(JsonmodelMeta, object)):

    """Base class for all models."""

    def __init__(self, **kwargs):
        self._cache_key = _CacheKey()
        self.populate(**kwargs)

    def populate(self, **values):
        """Populate values to fields. Skip non-existing."""
        values = values.copy()
        for attr_name, structure_name, field in self.iterate_with_name():
            # set field by structure name
            if structure_name in values:
                field.__set__(self, values.pop(structure_name))
            elif attr_name in values:
                field.__set__(self, values.pop(attr_name))

    @classmethod
    def get_field(cls, field_name):
        """Get field associated with given attribute."""
        field = getattr(cls, field_name, None)
        if isinstance(field, BaseField):
            return field
        else:
            raise errors.FieldNotFound('Field not found', field_name)

    def __iter__(self):
        """Iterate through fields and values."""
        yield from self.iterate_over_fields()

    def validate(self):
        """Explicitly validate all the fields."""
        for attr_name, field in self:
            try:
                field.validate_for_object(self)
            except ValidationError as error:
                raise ValidationError(
                    'Error for field {attr_name!r}: {error}'
                    .format(attr_name=attr_name, error=error)
                )

    @classmethod
    def iterate_over_fields(cls):
        """Iterate through fields as `(attribute_name, field_instance)`."""
        for attr_name in dir(cls):
            field = getattr(cls, attr_name)
            if isinstance(field, BaseField):
                yield attr_name, field

    @classmethod
    def iterate_with_name(cls):
        """Iterate over fields, but also give `structure_name`.

        Format is `(attribute_name, structure_name, field_instance)`.
        Structure name is name under which value is seen in structure and
        schema (in primitives) and only there.
        """
        for attr_name, field in cls.iterate_over_fields():
            structure_name = field.structure_name(attr_name)
            yield attr_name, structure_name, field

    def to_struct(self):
        """Cast model to Python structure."""
        return parsers.to_struct(self)

    @classmethod
    def to_json_schema(cls):
        """Generate JSON schema for model."""
        return parsers.to_json_schema(cls)

    def __repr__(self):
        attrs = {}
        for attr_name, field in self:
            try:
                attr = getattr(self, attr_name)
                if attr is not None:
                    attrs[attr_name] = repr(attr)
            except ValidationError:
                pass

        return '{class_name}({fields})'.format(
            class_name=self.__class__.__name__,
            fields=', '.join(
                '{0[0]}={0[1]}'.format(x) for x in sorted(attrs.items())
            ),
        )

    def __str__(self):
        return '{name} object'.format(name=self.__class__.__name__)

    def __setattr__(self, name, value):
        try:
            return super(Base, self).__setattr__(name, value)
        except ValidationError as error:
            raise ValidationError(
                "Error for field '{name}'.".format(name=name),
                error
            )

    def __eq__(self, other):
        if type(other) is not type(self):
            return False

        for attr_name, _ in self.iterate_over_fields():
            try:
                our = getattr(self, attr_name)
            except errors.ValidationError:
                our = None

            try:
                their = getattr(other, attr_name)
            except errors.ValidationError:
                their = None

            if our != their:
                return False

        return True

    def __ne__(self, other):
        return not (self == other)


class _CacheKey(object):
    """Object to identify model in memory."""
    pass
