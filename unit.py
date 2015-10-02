# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import re
import logging

from decimal import Decimal


logger = logging.getLogger(__name__)

r = lambda exp: re.compile(exp, flags=re.IGNORECASE)

RE_NUM = r"[^\.\B](\d+(?:[\d ',\.]?\d)*)"


# ######################################
# Constants

LENGTH = 'length'
MASS = 'mass'
VOLUME = 'volume'
VELOCITY = 'velocity'
TIME = 'time'
POWER = 'power'

METERS = 'meters'
KILOMETERS = 'kilometers'
INCHES = 'inches'
MILES = 'miles'
YARDS = 'yards'
FEET = 'feet'
FT_IN = 'feet inches'

KILOGRAMS = 'kilograms'
POUNDS = 'pounds'

CUBIC_METERS = 'cubic meters'
LITERS = 'liters'
FL_OZ = 'fl oz'
GALLONS = 'gallons'

M_S = 'm/s'
KPH = 'kph'
MPH = 'mph'

SECONDS = 'seconds'
MINUTES = 'minutes'
HOURS = 'hours'
DAYS = 'days'
WEEKS = 'weeks'
MONTHS = 'months'

KILOWATTS = 'kilowatts'
WATTS = 'watts'
HP = 'hp'

UNITS = {
    # normalize to meter
    LENGTH: [
        (r(RE_NUM + r'(?:m| meters?|metres?)\b'), METERS, Decimal('1')),
        (r(RE_NUM + r'(?:km| kilometers?|kilometres?)\b'), KILOMETERS, Decimal('1000')),
        (r(RE_NUM + r' ?(?:inch|inches)\b'), INCHES, Decimal('0.0254')),
        (r(RE_NUM + r' ?mi(?:les?)?(?! per)\b'), MILES, Decimal('1609.34')),
        (r(RE_NUM + r' (?:yards?|yd)\b'), YARDS, Decimal('0.9144')),
        (r(RE_NUM + r' ?(?:feet|ft)\b'), FEET, Decimal('0.3048')),
        (r(r'(\d)\'(\d{,2})"'), FT_IN,
            lambda ft, i: ft * Decimal('0.3048') + i * Decimal('0.0254')),
    ],
    # normalize to kilogram
    MASS: [
        (r(RE_NUM + r'(?:kg| kilogram[m|s]?| kilos?)\b'), KILOGRAMS, Decimal('1')),
        (r(RE_NUM + r' ?(?:lbs?|pounds?)\b'), POUNDS, Decimal('0.453592')),
    ],
    # normalize to cubic meter
    VOLUME: [
        (r(RE_NUM + r' ?(?:m3|m³)\b'), CUBIC_METERS, Decimal('1')),
        (r(RE_NUM + r'(?:l| liters?|litres?)\b'), LITERS, Decimal('1000')),
        (r(RE_NUM + r' ?(?:oz\.?|fl\.? ?oz\.?|ounces?|fl\.? ?ounces?|fluid ?oz\.?|fluid ?ounces?)\b'),  # noqa
            FL_OZ, Decimal('0.0000295735')),
        (r(RE_NUM + r' ?gallons?\b'), GALLONS, Decimal('0.00378541')),
    ],
    # normalize to meters per second
    VELOCITY: [
        (r(RE_NUM + r' ?(?:m/s|meters? / second|meters? per second)\b'), M_S, Decimal('1')),
        (r(RE_NUM + r' ?(?:kilometers per hour|kilometres per hour|kph|km/?h)\b'), KPH, Decimal('0.277778')),
        (r(RE_NUM + r' ?(?:miles per hour|mph)\b'), MPH, Decimal('0.44704')),
    ],
    # normalize to seconds
    TIME: [
        (r(RE_NUM + r' ?seconds\b'), SECONDS, Decimal('1')),
        (r(RE_NUM + r' ?minutes\b'), MINUTES, Decimal('60')),
        (r(RE_NUM + r' ?(?:hours|hrs)\b'), HOURS, Decimal('3600')),
        (r(RE_NUM + r' ?days\b'), DAYS, Decimal('86400')),
        (r(RE_NUM + r' ?(?:weeks|wks)\b'), WEEKS, Decimal('604800')),
        (r(RE_NUM + r' ?months\b'), MONTHS, Decimal('2592000')),
    ],
    # normalize to kilowatts
    POWER: [
        (r(RE_NUM + r' ?(?:kw|kilowatts?)\b'), KILOWATTS, Decimal('1')),
        (r(RE_NUM + r' ?watts?\b'), WATTS, Decimal('1000')),
        (r(RE_NUM + r' ?(?:hp|bhp|whp)\b'), HP, Decimal('0.745699872')),
    ],
    # IDEAS: gas mileage
}

BLACKLIST = [
    '1ft',
    '1 ft',
    '2 feet',
    '9 yards',  # silly movies
    '1000 yard stare',
    '8 mile',  # more movies
    '24 hour',
    '24 hours',
    '1 day',
    '7 days',
    '30 days',
    '365 days',
    '12 months',
]

USELESS_UNITS = {
    LENGTH: [
        (['beard-minutes'], lambda l: l * Decimal('1666666.66667')),
        (['beard-hours'], lambda l: l * Decimal('27777.7777778')),
        (['attoparsec', 'attoParsecs'], lambda l: l * Decimal('32.4077929')),
        (['pico light seconds'], lambda l: l * Decimal('3335.55703803')),
        (['smoot'], lambda l: l * Decimal('0.587613116')),
    ],
    MASS: [
        (['zepto-jupiters', 'zepto jupiter mass'], lambda m: m * Decimal('5.2665e-7')),
        (['dynes'], lambda m: m * Decimal('980665')),
        (['cement bags'], lambda m: m * Decimal('0.02345')),
    ],
    VOLUME: [
        (['barn megaparsecs', 'barn-megaparsec'], lambda v: v * Decimal('324078')),
        (['Hubble-barn'], lambda v: v * Decimal('76.6')),
        (['acre-feet'], lambda v: v * Decimal('0.000810713194')),
    ],
    VELOCITY: [
        # TODO: randomly select length/time units
        (['attoParsecs / microfortnight', 'attoparsec per microfortnight'], lambda v: v * Decimal('39.2004663')),
        (['smoots / nanocentury', 'smoot per nanocentury'], lambda v: v * Decimal('1.854')),
        (['light seconds / dog year', 'light-seconds per dog year'], lambda v: v * Decimal('0.01503')),
    ],
    TIME: [
        (['microcenturies'], lambda t: t * Decimal('0.0003169')),
        (['nanocenturies'], lambda t: t * Decimal('0.3169')),
        (['microfortnights'], lambda t: t * Decimal('0.8267')),
        (['dog years'], lambda t: t * Decimal('2.21967699e-7')),
    ],
    POWER: [
        (['donkey power', 'brake donkey power'], lambda p: p * Decimal('4.00')),
    ],
}

NAMES = {
    METERS: 'meters',
    KILOMETERS: 'kilometers',
    INCHES: 'inches',
    MILES: 'miles',
    YARDS: 'yards',
    FEET: 'feet',
    FT_IN: 'feet inches',

    KILOGRAMS: 'kilograms',
    POUNDS: 'pounds',

    CUBIC_METERS: 'cubic meters',
    LITERS: 'liters',
    FL_OZ: 'fl oz',
    GALLONS: 'gallons',

    M_S: 'm/s',
    KPH: 'kph',
    MPH: 'mph',

    SECONDS: 'seconds',
    MINUTES: 'minutes',
    HOURS: 'hours',
    DAYS: 'days',
    WEEKS: 'weeks',
    MONTHS: 'months',

    KILOWATTS: 'kilowatts',
    WATTS: 'watts',
    HP: 'hp',
}


def _parse_num(text):
    """Treat dots as decimal separators."""
    cleaned = text.replace(',', '').replace(' ', '').replace("'", '')
    return Decimal(cleaned)


class Unit(object):
    """
    A single unit with value.

    """
    def __init__(self, category, value, unit=None, original=None):
        if category not in UNITS.keys():
            raise TypeError('unknown unit category {}'.format(category))
        self.category = category
        self.value = value
        self.unit = unit
        self.original = original

    def __repr__(self):
        if self.is_original():
            fmt = '<Unit(category={category!r}, value={value!r}, unit={unit!r})>'
        else:
            fmt = '<Unit(category={category!r}, value={value!r}, original={original!r})>'
        return fmt.format(**self.__dict__)

    def is_original(self):
        return self.unit is not None

    @staticmethod
    def find_units(text):
        """
        Find all mentioned units in a text.

        """
        for category, units in UNITS.items():
            for regex, unit, normal in units:
                matches = list(regex.finditer(text))
                for match in matches:
                    if match.group(0).lower() in BLACKLIST:
                        continue

                    raw_values = map(_parse_num, match.groups())
                    if callable(normal):
                        value = normal(*raw_values)
                    else:
                        value = raw_values[0] * normal

                    original = Unit(category, raw_values, unit=unit)
                    yield Unit(category, value, original=original)