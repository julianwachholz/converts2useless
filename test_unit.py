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
    ('123456', Decimal(123456)),
    ('60,018', Decimal(60018)),
    ('70 018', Decimal(70018)),
    ('160,018', Decimal(160018)),
    ('43,778,147.0000016', Decimal('43778147.0000016')),
])
@pytest.mark.parametrize('unit,templates', [
    (unit.METERS, ['{} meter', '{}metres']),
    (unit.KILOMETERS, ['{}km', '{} kilometer', '{}kilometres']),
    (unit.INCHES, ['{} inches', '{}inch', '{}in', '{}" wide']),
    (unit.MILES, ['{} miles', '{}mi']),
    (unit.YARDS, ['{} yards', '{}yd']),
    (unit.FEET, ['{} feet', '{}ft', "{}' long"]),

    (unit.KILOGRAMS, ['{}kg', '{} kilogram']),
    (unit.POUNDS, ['{}lb', '{} pounds', '{} lbs']),

    (unit.CUBIC_METERS, ['{}m^3', '{} cubic meters']),
    (unit.LITERS, ['{} liters', '{} litres']),
    (unit.FL_OZ, ['{}fl.oz.', '{} fluid ounces']),
    (unit.GALLONS, ['{}gal', '{} gallons']),

    (unit.M_S, ['{}m/s', '{} meters/second']),
    (unit.KPH, ['{} kph', '{}km/h', '{} kilometers per hour']),
    (unit.MPH, ['{}mph', '{} mph', '{} miles an hour']),

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
def test_unit_detection(value, expected, unit, templates):
    """Testing different combinations of number formats and all units."""
    for template in templates:
        text = template.format(value)
        found_unit = Unit.find_first_unit(text)
        assert found_unit is not None, 'Nothing found in {!r}'.format(text)
        assert found_unit.value == expected and found_unit.unit == unit
        assert isinstance(found_unit.to_useless(), type(''))


@pytest.mark.parametrize('text,expected_units', [
    ("I walked 12 miles to have 5 minutes of peace.",
        [Unit(unit.LENGTH, 12, unit=unit.MILES), Unit(unit.TIME, 5, unit=unit.MINUTES)]),
    ("17 minutes into 8 Mile and I already love it.",
        [Unit(unit.TIME, 17, unit=unit.MINUTES)]),
    ("this car makes 859 horse power at the wheels",
        [Unit(unit.POWER, 859, unit=unit.HP)]),
    ("2 hours ago, this was 7 minutes long",
        [Unit(unit.TIME, 2, unit=unit.HOURS), Unit(unit.TIME, 7, unit=unit.MINUTES)]),
    ("my gf is only 4'7\"",
        [[Unit(unit.LENGTH, 4, unit=unit.FEET), Unit(unit.LENGTH, 7, unit=unit.INCHES)]]),
    ("the movie runs for 2 hours and 7 minutes",
        [[Unit(unit.TIME, 2, unit=unit.HOURS), Unit(unit.TIME, 7, unit=unit.MINUTES)]]),
    ("I have waited 1 hour, 12 minutes and 7 seconds",
        [[Unit(unit.TIME, 1, unit=unit.HOURS), Unit(unit.TIME, 12, unit=unit.MINUTES), Unit(unit.TIME, 7, unit=unit.SECONDS)]]),  # noqa
    ("ships passed within 12 nautical miles of the U.S.-held Aleutian Islands off Alaska In September",
        [Unit(unit.LENGTH, 12, unit=unit.NAUT_MILES)]),
    ("you might as well go 0 mph", []),
    ("Only us true 90's kids played it like that.", []),
    ("they just want to press \"4\", \"3\" maybe  \"w\" and win.", []),
])
def test_text_detection(text, expected_units):
    """Make sure we detect all mentioned units anywhere in a text."""
    found_units = list(Unit.find_units(text))
    assert found_units == expected_units


@pytest.mark.parametrize('values,expected', [
    (['6', '8'], [Decimal(6), Decimal(8)]),
    (['822', '908'], [Decimal(822), Decimal(908)]),
    (['1,042', '3.5'], [Decimal(1042), Decimal('3.5')]),
])
@pytest.mark.parametrize('units,template', [
    ((unit.FEET, unit.INCHES), '{0}\'{1}"'),
    ((unit.FEET, unit.INCHES), '{0}ft {1}in'),
    ((unit.MINUTES, unit.SECONDS), '{0} minutes {1} seconds'),
    ((unit.HOURS, unit.MINUTES), '{0} hours {1} minutes'),
    ((unit.HOURS, unit.MINUTES), '{0} hrs {1} minutes'),
])
def test_compound_units(values, expected, units, template):
    """Testing arbitrary compound unit formats."""
    text = template.format(*values)
    found_units = Unit.find_first_unit(text)

    assert found_units is not None
    assert isinstance(found_units, list)

    for i, found_unit in enumerate(found_units):
        assert found_unit.unit == units[i]
        assert found_unit.value == expected[i]
        assert isinstance(found_unit.to_useless(), type(''))


@pytest.mark.parametrize('unit1,unit2', [
    (Unit(unit.LENGTH, Decimal(300), unit=unit.KILOMETERS), Unit(unit.LENGTH, Decimal(300000), unit=unit.METERS)),
    (Unit(unit.LENGTH, Decimal(25), unit=unit.YARDS), Unit(unit.LENGTH, Decimal('22.86'), unit=unit.METERS)),
    (Unit(unit.MASS, Decimal(1500), unit=unit.POUNDS), Unit(unit.MASS, Decimal('680.39'), unit=unit.KILOGRAMS)),
    (Unit(unit.VOLUME, Decimal('0.03275'), unit=unit.LITERS), Unit(unit.VOLUME, Decimal('0.033'), unit=unit.LITERS)),
])
def test_normalize(unit1, unit2):
    """Conversion in the same category but with different units should work."""
    assert unit1 == unit2
