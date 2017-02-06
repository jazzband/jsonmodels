# -*- coding: utf-8 -*-
import datetime

from jsonmodels.fields import DateTimeField
from jsonmodels.models import Base


def test_datetime_field_is_not_none():
    d = datetime.datetime.now()

    class Model(Base):
        datetime_field = DateTimeField()

    model = Model(
            datetime_field=d
    )

    struct_model = model.to_struct()

    assert struct_model.get('datetime_field') == d


def test_datetime_field_is_none():
    class Model(Base):
        datetime_field = DateTimeField()

    model = Model()

    struct_model = model.to_struct()

    assert struct_model.get('datetime_field') is None
