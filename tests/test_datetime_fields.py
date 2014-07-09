"""Tests for datetime related fields."""

import datetime
import unittest

from dateutil.tz import tzoffset

from jsonmodels import models, fields, error


class _TestCet(datetime.tzinfo):

    def tzname(self):
        return 'CET'

    def utcoffset(self, dt):
        return datetime.timedelta(hours=2)

    def dst(self, dt):
        return datetime.timedelta(0)


class _TestUtc(datetime.tzinfo):

    def tzname(self):
        return 'UTC'

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)


class TimeFieldTestCase(unittest.TestCase):

    def test_time_field(self):

        class Event(models.Base):

            time = fields.TimeField()

        event = Event()
        event.validate()

        event.time = '12:03:34'
        self.assertRaises(error.ValidationError, event.validate)

        event.time = datetime.time()
        event.validate()

    def test_time_field_to_struct(self):

        field = fields.TimeField()

        self.assertIsNone(field.str_format)

        tt = datetime.time()
        self.assertEqual('00:00:00', field.to_struct(tt))

        tt = datetime.time(12, 34, 56)
        self.assertEqual('12:34:56', field.to_struct(tt))

    def test_time_field_to_struct_with_format(self):

        field = fields.TimeField(str_format='%H:%M')

        self.assertEqual('%H:%M', field.str_format)

        tt = datetime.time()
        self.assertEqual('00:00', field.to_struct(tt))

        tt = datetime.time(12, 34, 56)
        self.assertEqual('12:34', field.to_struct(tt))

    def test_time_field_to_struct_with_tz(self):

        field = fields.TimeField()

        tt = datetime.time(tzinfo=_TestCet())
        self.assertEqual('00:00:00+02:00', field.to_struct(tt))

        tt = datetime.time(12, 34, 56, tzinfo=_TestCet())
        self.assertEqual('12:34:56+02:00', field.to_struct(tt))

        tt = datetime.time(tzinfo=_TestUtc())
        self.assertEqual('00:00:00+00:00', field.to_struct(tt))

        tt = datetime.time(12, 34, 56, tzinfo=_TestUtc())
        self.assertEqual('12:34:56+00:00', field.to_struct(tt))

    def test_time_field_format_has_precedence(self):

        field = fields.TimeField(str_format='%H:%M')

        tt = datetime.time(12, 34, 56, tzinfo=_TestCet())
        self.assertEqual('12:34', field.to_struct(tt))

    def test_time_field_parse_value(self):

        field = fields.TimeField()

        self.assertEqual(datetime.time(), field.parse_value('00:00:00'))
        self.assertEqual(
            datetime.time(2, 34, 45, tzinfo=tzoffset(None, 7200)),
            field.parse_value('2:34:45+02:00'),
        )

        self.assertRaises(TypeError, field.parse_value, 'not a time')


class DateFieldTestCase(unittest.TestCase):

    def test_date_field(self):

        class Event(models.Base):

            date = fields.DateField()

        event = Event()
        event.validate()

        event.date = '2014-04-21'
        self.assertRaises(error.ValidationError, event.validate)

        event.date = datetime.date(2014, 4, 21)
        event.validate()

    def test_date_field_to_struct(self):

        field = fields.DateField()

        self.assertIsNone(field.str_format)

        tt = datetime.date(2000, 1, 1)
        self.assertEqual('2000-01-01', field.to_struct(tt))

        tt = datetime.date(2491, 5, 6)
        self.assertEqual('2491-05-06', field.to_struct(tt))

    def test_date_field_to_struct_with_format(self):

        field = fields.DateField(str_format='%Y/%m/%d')

        self.assertEqual('%Y/%m/%d', field.str_format)

        tt = datetime.date(2244, 5, 7)
        self.assertEqual('2244/05/07', field.to_struct(tt))

    def test_date_field_parse_value(self):

        field = fields.DateField()

        self.assertEqual(
            datetime.date(2012, 12, 21),
            field.parse_value('2012-12-21'),
        )
        self.assertEqual(
            datetime.date(2014, 4, 21),
            field.parse_value('2014-04-21'),
        )

        self.assertRaises(TypeError, field.parse_value, 'not a date')


class DateTimeFieldTestCase(unittest.TestCase):

    def test_datetime_field(self):

        class Event(models.Base):

            date = fields.DateTimeField()

        event = Event()
        event.validate()

        event.date = '2013-05-06 12:03:34'
        self.assertRaises(error.ValidationError, event.validate)

        event.date = datetime.datetime.now()
        event.validate()

    def test_datetime_field_to_struct(self):

        field = fields.DateTimeField()

        self.assertIsNone(field.str_format)

        tt = datetime.datetime(2014, 5, 7, 12, 45, 56)
        self.assertEqual('2014-05-07T12:45:56', field.to_struct(tt))

    def test_datetime_field_to_struct_with_format(self):

        field = fields.TimeField(str_format='%H:%M %Y/%m')

        self.assertEqual('%H:%M %Y/%m', field.str_format)

        tt = datetime.datetime(2014, 5, 7, 12, 45, 56)
        self.assertEqual('12:45 2014/05', field.to_struct(tt))

    def test_datetime_field_to_struct_with_tz(self):

        field = fields.DateTimeField()

        tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestCet())
        self.assertEqual('2014-05-07T12:45:56+02:00', field.to_struct(tt))

        tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestUtc())
        self.assertEqual('2014-05-07T12:45:56+00:00', field.to_struct(tt))

    def test_datetime_field_format_has_precedence(self):

        field = fields.DateTimeField(str_format='%H:%M %Y/%m')

        tt = datetime.datetime(2014, 5, 7, 12, 45, 56, tzinfo=_TestCet())
        self.assertEqual('12:45 2014/05', field.to_struct(tt))

    def test_datetime_field_parse_value(self):

        field = fields.DateTimeField()

        self.assertEqual(
            datetime.datetime(2014, 4, 21, 12, 45, 56),
            field.parse_value('2014-04-21T12:45:56'),
        )
        self.assertEqual(
            datetime.datetime(
                2014, 4, 21, 12, 45, 56, tzinfo=tzoffset(None, 7200)),
            field.parse_value('2014-04-21T12:45:56+02:00'),
        )

        self.assertRaises(TypeError, field.parse_value, 'not a datetime')
