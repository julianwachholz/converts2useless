#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
"""
Tests for the Unit class and utility methods.

"""
from decimal import Decimal

import pytest

import unit
from unit import Unit


@pytest.mark.parametrize('value,expected', [
    ('42', Decimal(42)),
    ('1234', Decimal(1234)),
    ('12345', Decimal(12345)),
    ('123456', Decimal(123456)),
    ('60,018', Decimal(60018)),
    ('70 018', Decimal(70018)),
    ("80'018", Decimal(80018)),
    ('160,018', Decimal(160018)),
    ('43,778,147.0000016', Decimal('43778147.0000016')),
])
@pytest.mark.parametrize('unit,formats', [
    (unit.METERS, ['{} meter', '{}metres']),
    pytest.mark.xfail((unit.M_S, ['{} meter', '{}metres'])),
    (unit.KILOMETERS, ['{}km', '{} kilometer', '{}kilometres']),
    pytest.mark.xfail((unit.KPH, ['{}km', '{} kilometer', '{}kilometres'])),
    (unit.INCHES, ['{} inches', '{}inch']),
    (unit.MILES, ['{} miles', '{}mi']),
    pytest.mark.xfail((unit.MPH, ['{} miles', '{}mi'])),
    (unit.YARDS, ['{} yards', '{}yd']),
    (unit.FEET, ['{} feet', '{}ft']),
    pytest.mark.xfail((unit.FEET, ['{} foot'])),
    # (unit.FT_IN, ['{} miles', '{}mi']),  # TODO special case

    (unit.KILOGRAMS, ['{}kg', '{} kilogram']),
    (unit.POUNDS, ['{}lb', '{} pounds', '{} lbs']),

    (unit.CUBIC_METERS, ['{}m^3', '{} cubic meters']),
    (unit.LITERS, ['{} liters', '{} litres', '{}l']),
    pytest.mark.xfail((unit.LITERS, ['{} l'])),
    (unit.FL_OZ, ['{}fl.oz.', '{} fluid ounces']),
    (unit.GALLONS, ['{}gal', '{} gallons']),

    (unit.M_S, ['{}m/s', '{} meters/second']),
    pytest.mark.xfail((unit.METERS, ['{}m/s', '{} meters/second'])),
    (unit.KPH, ['{} kph', '{}km/h', '{} kilometers per hour']),
    pytest.mark.xfail((unit.KILOMETERS, ['{} kph', '{}km/h', '{} kilometers per hour'])),
    (unit.MPH, ['{}mph', '{} mph', '{} miles an hour']),
    pytest.mark.xfail((unit.MPH, ['{}mph', '{} mph', '{} miles an hour'])),

    (unit.SECONDS, ['{} seconds']),
    (unit.MINUTES, ['{} minutes']),
    (unit.HOURS, ['{}hrs', '{} hours']),
    (unit.DAYS, ['{} days']),
    (unit.WEEKS, ['{} weeks', '{}wks']),
    (unit.MONTHS, ['{} months']),

    (unit.KILOWATTS, ['{}kW', '{} kilowatt']),
    (unit.WATTS, ['{} watt', '{} watts']),
    (unit.HP, ['{}HP', '{} WHP', '{} horsepower']),
])
def test_unit_detection(value, expected, unit, formats):
    for template in formats:
        text = template.format(value)
        found_unit = Unit.find_first_unit(text)
        assert found_unit is not None
        assert found_unit.value == expected and found_unit.unit == unit
