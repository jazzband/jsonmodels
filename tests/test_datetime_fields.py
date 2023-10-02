import datetime

import pytest
from dateutil.tz import tzoffset

from jsonmodels import fields, models


class _TestCet(datetime.tzinfo):
    def tzname(self):
        return "CET"

    def utcoffset(self, dt):
        return datetime.timedelta(hours=2)

    def dst(self, dt):
        return datetime.timedelta(0)


class _TestUtc(datetime.tzinfo):
    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)


def test_time_field():
    class Event(models.Base):
        time = fields.TimeField()

    event = Event()

    event.time = "12:03:34"
    assert isinstance(event.time, datetime.time)
    event.time = datetime.time()


def test_time_field_not_required():
    class Event(models.Base):
        time = fields.TimeField(required=False)

    event = Event()

    event.time = None
    assert event.time is None


def test_time_field_to_struct():
    field = fields.TimeField()

    assert field.str_format is None

    tt = datetime.time()
    assert "00:00:00" == field.to_struct(tt)

    tt = datetime.time(12, 34, 56)
    assert "12:34:56" == field.to_struct(tt)


def test_base_field_to_struct():
    field = fields.BaseField()
    assert field.to_struct(True) is True
    assert field.to_struct(False) is False
    assert field.to_struct("chuck") == "chuck"
    assert field.to_struct(1) == 1


def test_time_field_to_struct_with_format():
    field = fields.TimeField(str_format="%H:%M")

    assert "%H:%M" == field.str_format

    tt = datetime.time()
    assert "00:00" == field.to_struct(tt)

    tt = datetime.time(12, 34, 56)
    assert "12:34" == field.to_struct(tt)


def test_time_field_to_struct_with_tz():
    field = fields.TimeField()

    tt = datetime.time(tzinfo=_TestCet())
    assert "00:00:00+02:00" == field.to_struct(tt)

    tt = datetime.time(12, 34, 56, tzinfo=_TestCet())
    assert "12:34:56+02:00" == field.to_struct(tt)

    tt = datetime.time(tzinfo=_TestUtc())
    assert "00:00:00+00:00" == field.to_struct(tt)

    tt = datetime.time(12, 34, 56, tzinfo=_TestUtc())
    assert "12:34:56+00:00" == field.to_struct(tt)


def test_time_field_format_has_precedence():
    field = fields.TimeField(str_format="%H:%M")

    tt = datetime.time(12, 34, 56, tzinfo=_TestCet())
    assert "12:34" == field.to_struct(tt)


def test_time_field_parse_value():
    field = fields.TimeField()

    assert datetime.time() == field.parse_value("00:00:00")
    assert datetime.time(2, 34, 45, tzinfo=tzoffset(None, 7200)) == field.parse_value(
        "2:34:45+02:00"
    )

    with pytest.raises(ValueError):
        field.parse_value("not a time")


def test_date_field():
    class Event(models.Base):
        date = fields.DateField()

    event = Event()

    event.date = "2014-04-21"
    assert isinstance(event.date, datetime.date)
    event.date = datetime.date(2014, 4, 21)


def test_date_field_not_required():
    class Event(models.Base):
        date = fields.DateField(required=False)

    event = Event()

    event.date = None
    assert event.date is None


def test_date_field_to_struct():
    field = fields.DateField()

    assert field.str_format is None

    tt = datetime.date(2000, 1, 1)
    assert "2000-01-01" == field.to_struct(tt)

    tt = datetime.date(2491, 5, 6)
    assert "2491-05-06" == field.to_struct(tt)


def test_date_field_to_struct_with_format():
    field = fields.DateField(str_format="%Y/%m/%d")

    assert "%Y/%m/%d" == field.str_format

    tt = datetime.date(2244, 5, 7)
    assert "2244/05/07" == field.to_struct(tt)


def test_date_field_parse_value():
    field = fields.DateField()

    assert datetime.date(2012, 12, 21) == field.parse_value("2012-12-21")
    assert datetime.date(2014, 4, 21) == field.parse_value("2014-04-21")

    with pytest.raises(ValueError):
        field.parse_value("not a date")


def test_datetime_field():
    class Event(models.Base):
        date = fields.DateTimeField()

    event = Event()
    event.date = "2013-05-06 12:03:34"

    assert isinstance(event.date, datetime.datetime)
    event.date = datetime.datetime.now()


def test_datetime_field_not_required():
    class Event(models.Base):
        date = fields.DateTimeField()

    event = Event()
    event.date = None
    assert event.date is None


def test_datetime_field_to_struct():
    field = fields.DateTimeField()

    assert field.str_format is None

    tt = datetime.datetime(2014, 5, 7, 12, 45, 56)
    assert "2014-05-07T12:45:56" == field.to_struct(tt)


def test_datetime_field_to_struct_with_format():
    field = fields.TimeField(str_format="%H:%M %Y/%m")

    assert "%H:%M %Y/%m" == field.str_format

    tt = datetime.datetime(2014, 5, 7, 12, 45, 56)
    assert "12:45 2014/05" == field.to_struct(tt)


def test_datetime_field_to_struct_with_tz():
    field = fields.DateTimeField()

    tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestCet())
    assert "2014-05-07T12:45:56+02:00" == field.to_struct(tt)

    tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestUtc())
    assert "2014-05-07T12:45:56+00:00" == field.to_struct(tt)


def test_datetime_field_format_has_precedence():
    field = fields.DateTimeField(str_format="%H:%M %Y/%m")

    tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestCet())
    assert "12:45 2014/05" == field.to_struct(tt)


def test_datetime_field_parse_value():
    field = fields.DateTimeField()

    assert datetime.datetime(2014, 4, 21, 12, 45, 56) == field.parse_value(
        "2014-04-21T12:45:56"
    )
    assert datetime.datetime(
        2014, 4, 21, 12, 45, 56, tzinfo=tzoffset(None, 7200)
    ) == field.parse_value("2014-04-21T12:45:56+02:00")

    with pytest.raises(ValueError):
        field.parse_value("not a datetime")


def test_datetime_field_is_none():
    """If field nullable, dateutil raises error"""

    datetime_field = fields.DateTimeField()

    assert datetime_field.parse_value(None) is None
