from . import errors, parsers
from .errors import ValidationError
from .fields import BaseField


class JsonmodelMeta(type):
    def __new__(cls, name, bases, attributes):
        cls.validate_fields(attributes)
        return super(cls, cls).__new__(cls, name, bases, attributes)

    @staticmethod
    def validate_fields(attributes):
        fields = {
            key: value
            for key, value in attributes.items()
            if isinstance(value, BaseField)
        }
        taken_names = set()
        for name, field in fields.items():
            structue_name = field.structue_name(name)
            if structue_name in taken_names:
                raise ValueError("Name taken", structue_name, name)
            taken_names.add(structue_name)


class Base(metaclass=JsonmodelMeta):

    """Base class for all models."""

    def __init__(self, **kwargs):
        self._cache_key = _CacheKey()
        self.populate(**kwargs)

    def populate(self, **values):
        """Populate values to fields. Skip non-existing."""
        values = values.copy()
        fields = list(self.iterate_with_name())
        for _, structure_name, field in fields:
            if structure_name in values:
                self.set_field(field, structure_name, values.pop(structure_name))
        for name, _, field in fields:
            if name in values:
                self.set_field(field, name, values.pop(name))

    def get_field(self, field_name):
        """Get field associated with given attribute."""
        for attr_name, field in self:
            if field_name == attr_name:
                return field

        raise errors.FieldNotFound("Field not found", field_name)

    def set_field(self, field, field_name, value):
        """Sets the value of a field."""
        try:
            field.__set__(self, value)
        except ValidationError as error:
            raise ValidationError(
                "Error for field '{name}': {error}.".format(
                    name=field_name, error=error
                )
            )

    def __iter__(self):
        """Iterate through fields and values."""
        yield from self.iterate_over_fields()

    def validate(self):
        """Explicitly validate all the fields."""
        for name, field in self:
            try:
                field.validate_for_object(self)
            except ValidationError as error:
                raise ValidationError(
                    f"Error for field '{name}'.",
                    error,
                )

    @classmethod
    def iterate_over_fields(cls):
        """Iterate through fields as `(attribute_name, field_instance)`."""
        for attr in dir(cls):
            clsattr = getattr(cls, attr)
            if isinstance(clsattr, BaseField):
                yield attr, clsattr

    @classmethod
    def iterate_with_name(cls):
        """Iterate over fields, but also give `structure_name`.

        Format is `(attribute_name, structue_name, field_instance)`.
        Structure name is name under which value is seen in structure and
        schema (in primitives) and only there.
        """
        for attr_name, field in cls.iterate_over_fields():
            structure_name = field.structue_name(attr_name)
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
        for name, _ in self:
            attr = getattr(self, name)
            if attr is not None:
                attrs[name] = repr(attr)

        return "{class_name}({fields})".format(
            class_name=self.__class__.__name__,
            fields=", ".join("{0[0]}={0[1]}".format(x) for x in sorted(attrs.items())),
        )

    def __str__(self):
        return f"{self.__class__.__name__} object"

    def __setattr__(self, name, value):
        try:
            return super().__setattr__(name, value)
        except ValidationError as error:
            raise ValidationError(f"Error for field '{name}'.", error)

    def __eq__(self, other):
        if type(other) is not type(self):
            return False

        for name, _ in self.iterate_over_fields():
            try:
                our = getattr(self, name)
            except errors.ValidationError:
                our = None

            try:
                their = getattr(other, name)
            except errors.ValidationError:
                their = None

            if our != their:
                return False

        return True

    def __ne__(self, other):
        return not (self == other)


class _CacheKey:
    """Object to identify model in memory."""
