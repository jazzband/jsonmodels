from jsonmodels import fields, models, validators


def test_bool_field():
    field = fields.BoolField()

    class Person(models.Base):
        is_programmer = field

    person = Person()
    assert person.is_programmer is None

    person.is_programmer = True
    assert person.is_programmer is True

    person.is_programmer = False
    assert person.is_programmer is False

    assert field.parse_value(True) is True
    assert field.parse_value("something") is True
    assert field.parse_value(object()) is True

    assert field.parse_value(None) is None

    assert field.parse_value(False) is False
    assert field.parse_value(0) is False
    assert field.parse_value("") is False
    assert field.parse_value([]) is False


def test_dict_field():
    field = fields.DictField()
    default_field = fields.DictField(
        default={"extra_default": "Hello", "deep_extra": {"spanish": "Hola"}},
        validators=[validators.Length(2)],
    )

    class Person(models.Base):
        extra = field
        extra_required = fields.DictField(required=True)
        extra_default = default_field
        extra_nullable = fields.DictField(nullable=True)

    person = Person(extra_required={"required": True})
    assert person.extra is None
    assert person.extra_required == {"required": True}
    assert person.extra_default == {
        "extra_default": "Hello",
        "deep_extra": {"spanish": "Hola"},
    }

    person.extra = {"extra": True}
    assert person.extra == {"extra": True}
