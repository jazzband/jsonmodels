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


class DateTimeFieldsTestCase(unittest.TestCase):

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
