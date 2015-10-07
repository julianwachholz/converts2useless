# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import re
import logging

from collections import OrderedDict
from decimal import Decimal
from random import choice


logger = logging.getLogger(__name__)


RE_NUM = r"\b((?:\d{1,3}(?:[ ,]\d{3})+|\d+)(?:\.\d+)?)"

r = lambda exp: re.compile(RE_NUM + exp, flags=re.IGNORECASE | re.MULTILINE)


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

###
# Format:
# {category: {unit: (regex, factor), ..}, ..}

UNIT_TABLE = {
    # normalize to meter
    LENGTH: OrderedDict([
        (KILOMETERS, (r(r'(?:km(?!/h)| ?kilometers?| ?kilometres?)(?! per| an| ?/ ?)\b'), Decimal('1000'))),
        (METERS, (r(r' ?(?:meters?|metres?)(?! per| an| ?/ ?)\b'), Decimal('1'))),
        (MILES, (r(r' ?mi(?:les?)?(?! per| an| ?/ ?)\b'), Decimal('1609.34'))),
        (YARDS, (r(r' ?(?:yards?|yd)\b'), Decimal('0.9144'))),
        (FEET, (r(r"(?:'[\B]?| ?feet\b| ?ft\b)"), Decimal('0.3048'))),
        (INCHES, (r(r'(?:"[\B]?|in\b| ?inch\b| ?inches\b)'), Decimal('0.0254'))),
    ]),
    # normalize to kilogram
    MASS: OrderedDict([
        (KILOGRAMS, (r(r'(?:kg| kilogram[m|s]?| kilos?)\b'), Decimal('1'))),
        (POUNDS, (r(r' ?(?:lbs?|pounds?)\b'), Decimal('0.453592'))),
    ]),
    # normalize to cubic meter
    VOLUME: OrderedDict([
        (CUBIC_METERS, (r(r' ?(?:m3|m³|m\^3|cubic meters?)\b'), Decimal('1'))),
        (LITERS, (r(r'(?:l| ?liters?| ?litres?)\b'), Decimal('0.001'))),
        (FL_OZ, (r(r' ?(?:oz\.?|fl\.? ?oz\.?|ounces?|fl\.? ?ounces?|fluid ?oz\.?|fluid ?ounces?)\b'), Decimal('0.0000295735'))),  # noqa
        (GALLONS, (r(r' ?gal(?:lons?)?\b'), Decimal('0.00378541'))),
    ]),
    # normalize to meters per second
    VELOCITY: OrderedDict([
        (M_S, (r(r' ?(?:m/s|meters? ?/ ?second|meters? (?:per|a) second)\b'), Decimal('1'))),
        (KPH, (r(r' ?(?:kilometers (?:per|an) hour|kilometres (?:per|an) hour|kph|km/?h)\b'), Decimal('0.277778'))),  # noqa
        (MPH, (r(r' ?(?:miles (?:per|an) hour|mph)\b'), Decimal('0.44704'))),
    ]),
    # normalize to seconds
    TIME: OrderedDict([
        (MONTHS, (r(r' ?months\b'), Decimal('2592000'))),
        (WEEKS, (r(r' ?(?:weeks|wks)\b'), Decimal('604800'))),
        (DAYS, (r(r' ?days\b'), Decimal('86400'))),
        (HOURS, (r(r' ?(?:hours?|hrs)\b'), Decimal('3600'))),
        (MINUTES, (r(r' ?minutes\b'), Decimal('60'))),
        (SECONDS, (r(r' ?seconds\b'), Decimal('1'))),
    ]),
    # normalize to kilowatts
    POWER: OrderedDict([
        (KILOWATTS, (r(r' ?(?:kW|kilowatts?)\b'), Decimal('1'))),
        (WATTS, (r(r' ?watts?\b'), Decimal('1000'))),
        (HP, (r(r' ?(?:hp|bhp|whp|horse ?power)\b'), Decimal('0.745699872'))),
    ]),
    # IDEAS: gas mileage, money
}

# compound unit chains, e.g. 5'4" or 3 minutes 12 seconds
UNIT_CHAINS = {
    LENGTH: [
        [FEET, INCHES],
    ],
    TIME: [
        [MINUTES, SECONDS],
        [HOURS, MINUTES, SECONDS],
    ],
}

CHAIN_WORDS = [
    'and',
    ',',
]


def _get_chain(category, unit, index):
    for chain in UNIT_CHAINS[category]:
        if len(chain) > index and chain[index] == unit:
            return chain


USELESS_UNITS = {
    LENGTH: [
        (['beard-minutes'], Decimal('1666666.66667')),
        (['beard-hours'], Decimal('27777.7777778')),
        (['attoparsec', 'attoParsecs'], Decimal('32.4077929')),
        (['pico light seconds'], Decimal('3335.55703803')),
        (['smoot'], Decimal('0.587613116')),
    ],
    MASS: [
        (['zepto-jupiters', 'zepto jupiter mass'], Decimal('5.2665e-7')),
        (['dynes'], Decimal('980665')),
        (['cement bags'], Decimal('0.02345')),
    ],
    VOLUME: [
        (['barn megaparsecs', 'barn-megaparsec'], Decimal('324078')),
        (['Hubble-barn'], Decimal('76.6')),
        (['acre-feet'], Decimal('0.000810713194')),
    ],
    VELOCITY: [
        # TODO: randomly select length/time units
        (['attoParsecs / microfortnight', 'attoparsec per microfortnight'], Decimal('39.2004663')),
        (['smoots / nanocentury', 'smoot per nanocentury'], Decimal('1.854')),
        (['light seconds / dog year', 'light-seconds per dog year'], Decimal('0.01503')),
    ],
    TIME: [
        (['microcenturies'], Decimal('0.0003169')),
        (['nanocenturies'], Decimal('0.3169')),
        (['microfortnights'], Decimal('0.8267')),
        (['dog years'], Decimal('2.21967699e-7')),
    ],
    POWER: [
        (['donkey power', 'brake donkey power'], Decimal('4.00')),
    ],
}

NAMES = {
    METERS: [' meters', 'm'],
    KILOMETERS: [' kilometers', 'km'],
    INCHES: [' inches', 'in'],
    MILES: [' miles', 'mi'],
    YARDS: [' yards', 'yd'],
    FEET: [' feet', 'ft'],
    (FEET, INCHES): [("'", '"'), ('feet', 'inches')],

    KILOGRAMS: [' kilograms', 'kg'],
    POUNDS: [' pounds', 'lb'],

    CUBIC_METERS: [' cubic meters', 'm^3'],
    LITERS: [' liters', 'l'],
    FL_OZ: [' fl oz', ' fluid ounces', 'fl.oz', ' fl.oz.'],
    GALLONS: [' gallons', 'gal'],

    M_S: ['m/s', ' meters per second'],
    KPH: ['kph', 'km/h', ' kilometers per hour'],
    MPH: ['mph', ' miles per hour'],

    SECONDS: [' seconds', 'secs'],
    MINUTES: [' minutes', 'mins'],
    HOURS: [' hours', 'hrs'],
    DAYS: [' days'],
    WEEKS: [' weeks', 'wks'],
    MONTHS: [' months'],

    KILOWATTS: [' kilowatts', 'kW'],
    WATTS: [' watts', 'W'],
    HP: ['hp', ' horsepower'],
}

BLACKLIST = [
    '1ft',
    '1 ft',
    '10ft',  # 10-foot pole
    '10 foot',
    '2 feet',
    '9 yards',  # whole nine yards
    '1000 yard',  # thousand-yard stare
    '8 mile',  # another movie
    '12oz',  # some graffiti community
    '24 hour',
    '24 hours',
    '1 day',
    '7 days',
    '30 days',
    '365 days',
    '12 months',
]


def _parse_num(text):
    """Treat dots as decimal separators."""
    cleaned = text.replace(',', '').replace(' ', '').replace("'", '')
    return Decimal(cleaned)


def prettify(value, places=6, sep=',', dp='.', pos='', neg='-'):
    q = Decimal(10) ** -places
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(neg if sign else pos)

    if value < 1:
        pass
    elif value < 10:
        result = result[places - 2:]
    elif value > 99000000:
        result = [' million'] + result[9 + places:]
    else:
        result = result[places + 1:]

    formatted = ''.join(reversed(result))
    if '.' in formatted:
        return formatted.rstrip('.0')
    return formatted


class Unit(object):
    """
    A unit that knows how to convert and normalize itself.

    """
    def __init__(self, category, value, unit=None, original=None):
        if category not in UNIT_TABLE.keys():
            raise TypeError('unknown unit category {}'.format(category))
        self.category = category
        if isinstance(value, int):
            value = Decimal(value)
        self.value = value
        self.unit = unit
        self.original = original

    def __repr__(self):
        if self.is_original():
            fmt = '<Unit(category={category!r}, value={value!r}, unit={unit!r})>'
        else:
            fmt = '<Unit(category={category!r}, value={value!r}, original={original!r})>'
        return fmt.format(**self.__dict__)

    def __str__(self):
        if self.unit is None:
            return '{!r} ({})'.format(self.value, self.category)
        return self.format_unit()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        normal = self.to_normal()
        other = other.to_normal()
        sig_figs = max(normal.value.as_tuple()[2], other.value.as_tuple()[2])
        quantum = Decimal('10') ** sig_figs
        normal_val = normal.value.quantize(quantum)
        other_val = other.value.quantize(quantum)

        if normal_val.normalize() == Decimal('0e0'):
            return False
        return normal.category == other.category and other_val == normal_val

    def format_unit(self):
        name = choice(NAMES[self.unit])
        return '{}{}'.format(prettify(self.value), name)

    def get_original_string(self):
        if self.is_original():
            return self.format_unit()
        if not self.original:
            return '[unknown] {} {}'.format(self.value, self.category)

        if isinstance(self.original, list):
            return ' '.join(map(str, self.original))
        return str(self.original)

    def is_original(self):
        return not self.is_normal()

    def is_normal(self):
        return self.unit is None

    def to_normal(self):
        if self.is_normal():
            return self

        normal_value = self.value * UNIT_TABLE[self.category][self.unit][1]
        return Unit(self.category, normal_value, original=self)

    def to_useless(self):
        """Convert the value to a randomly selected useless unit."""
        if self.is_original():
            return self.to_normal().to_useless()

        names, factor = choice(USELESS_UNITS[self.category])
        if callable(factor):
            value = factor(self.value)
        else:
            value = self.value * factor
        return '{} {}'.format(prettify(value), choice(names))

    @staticmethod
    def find_units(text):
        for category, units in UNIT_TABLE.items():
            look_for_chains = category in UNIT_CHAINS
            current_chain = None
            chain_units = []

            for unit, (regex, factor) in units.items():
                match = regex.search(text)
                if not match or match.group(0).lower().strip() in BLACKLIST:
                    continue

                raw_value = _parse_num(match.group(1))

                if raw_value <= 0:
                    continue

                unit_instance = Unit(category, raw_value, unit=unit)

                if look_for_chains:
                    current_chain = _get_chain(category, unit, len(chain_units))

                if current_chain and unit == current_chain[len(chain_units)]:
                    chain_units.append((unit_instance, match))

                elif not chain_units:
                    yield unit_instance

            if chain_units:
                if Unit._valid_chain(text, chain_units):
                    yield list(map(lambda u: u[0], chain_units))
                else:
                    for chain_unit, match in chain_units:
                        yield chain_unit

    @staticmethod
    def _valid_chain(text, chain):
        """Verify chains that the units are adjacent to each other."""
        if len(chain) < 2:
            return False

        offset = -1
        for unit, match in chain:
            if offset == -1:
                offset = match.end()
                continue

            gap_word = text[offset:match.start()].lower().strip()

            if gap_word and gap_word not in CHAIN_WORDS:
                return False
            offset = match.end()
        return True

    @staticmethod
    def find_normalized(text):
        units = list(Unit.find_units(text))
        for original in units:
            if isinstance(original, list):
                normal = reduce(lambda v, o: v + o.to_normal().value, original, Decimal())
                yield Unit(original[0].category, normal, original=original)
            else:
                yield original.to_normal()

    @staticmethod
    def find_first_unit(text):
        return next(Unit.find_units(text), None)
