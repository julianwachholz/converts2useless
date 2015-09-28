#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import random
from decimal import Decimal


r = lambda exp: re.compile(exp, flags=re.I)


BLACKLIST = [
    '1000 yard stare',
    '8 mile',
    '2 feet',
    '24 hour',
    '24 hours',
    '9 yards',
    '1 day',
    '1ft',
    '1 ft',
    '7 days',
    '30 days',
    '365 days',
    '12 months',
]

RE_NUM = r"\b(\d+[\d ,'\.]+)"

UNITS = [
    # normalize to meter
    ('length', [
        (r(RE_NUM + r'(?:m| meters?|metres?)\b'),
            lambda m: m * Decimal('1')),
        (r(RE_NUM + r'(?:km| kilometers?|kilometres?)\b'),
            lambda km: km * Decimal('1000')),
        (r(RE_NUM + r' ?(?:inch|inches)\b'),
            lambda i: i * Decimal('0.0254')),
        (r(RE_NUM + r' ?mi(?:les?)?(?! per)\b'),
            lambda mi: mi * Decimal('1609.34')),
        (r(RE_NUM + r' (?:yards?|yd)\b'),
            lambda y: y * Decimal('0.9144')),
        (r(RE_NUM + r' ?(?:feet|ft)\b'),
            lambda ft: ft * Decimal('0.3048')),
        (r(r'(\d)\'(\d{,2})"'),
            lambda ft, i: ft * Decimal('0.3048') + i * Decimal('0.0254')),
    ]),
    # normalize to kilogram
    ('mass', [
        (r(RE_NUM + r'(?:kg| kilogram[m|s]?| kilos?)\b'),
            lambda kg: kg * Decimal('1')),
        (r(RE_NUM + r' ?(?:lbs?|pounds?)\b'),
            lambda lb: lb * Decimal('0.453592')),
    ]),
    # normalize to cubic meter
    ('volume', [
        (r(RE_NUM + r' ?(?:m3|m³)\b'),
            lambda m3: m3 * Decimal('1')),
        (r(RE_NUM + r'(?:l| liters?|litres?)\b'),
            lambda l: l / Decimal('1000')),
        (r(RE_NUM + r' ?(?:oz\.?|fl\.? ?oz\.?|ounces?|fl\.? ?ounces?|fluid ?oz\.?|fluid ?ounces?)\b'),  # noqa
            lambda oz: oz * Decimal('0.0000295735')),
        (r(RE_NUM + r' ?gallons?\b'),
            lambda g: g * Decimal('0.00378541')),
    ]),
    # normalize to meters per second
    ('velocity', [
        (r(RE_NUM + r' ?(?:m/s|meters? / second|meters? per second)\b'),
            lambda ms: ms * Decimal('1')),
        (r(RE_NUM + r' ?(?:kilometers per hour|kilometres per hour|kph|km/?h)\b'),
            lambda kph: kph * Decimal('0.277778')),
        (r(RE_NUM + r' ?(?:miles per hour|mph)\b'),
            lambda mph: mph * Decimal('0.44704')),
    ]),
    # normalize to seconds
    ('time', [
        (r(RE_NUM + r' ?seconds\b'),
            lambda m: m * Decimal('1')),
        (r(RE_NUM + r' ?minutes\b'),
            lambda m: m * Decimal('60')),
        (r(RE_NUM + r' ?(?:hours|hrs)\b'),
            lambda m: m * Decimal('3600')),
        (r(RE_NUM + r' ?days\b'),
            lambda m: m * Decimal('86400')),
        (r(RE_NUM + r' ?(?:weeks|wks)\b'),
            lambda m: m * Decimal('604800')),
        (r(RE_NUM + r' ?months\b'),
            lambda m: m * Decimal('2592000')),
    ]),
    # normalize to kilowatts
    ('power', [
        (r(RE_NUM + r' ?(?:kw|kilowatts?)\b'),
            lambda w: w * Decimal('1')),
        (r(RE_NUM + r' ?watts?\b'),
            lambda w: w / Decimal('1000')),
        (r(RE_NUM + r' ?(?:hp|bhp|whp)\b'),
            lambda hp: hp * Decimal('0.745699872')),
    ]),
]


def parse_num(num):
    return Decimal(num.replace(',', '')
                      .replace(' ', '')
                      .replace("'", ''))

def get_units(text):
    """
    Get mentioned units and quantities from a comment body.

    """
    values = {}
    text = text.lower()
    for category, units in UNITS:
        for r, normalize in units:
            matches = list(r.finditer(text))
            for match in matches:
                if match.group(0).lower() in BLACKLIST:
                    continue
                groups = map(parse_num, match.groups())
                values[normalize(*groups)] = {
                    'category': category,
                    'original': match.group(0),
                }
    return values


# almost all definitions are computable on wolfram alpha
USELESS_UNITS = {
    'length': [
        (['beard-minutes'], lambda l: l * Decimal('1666666.66667')),
        (['beard-hours'], lambda l: l * Decimal('27777.7777778')),
        (['attoparsec', 'attoParsecs'], lambda l: l * Decimal('32.4077929')),
        (['pico light seconds'], lambda l: l / Decimal('0.0002998')),
        (['smoot'], lambda l: l * Decimal('0.587613116')),
    ],
    'mass': [
        (['zepto-jupiters', 'zepto jupiter mass'], lambda m: m * Decimal('5.2665e-7')),
        (['dynes'], lambda m: m * Decimal('980665')),
        (['cement bags'], lambda m: m / Decimal('42.6')),
    ],
    'volume': [
        (['barn megaparsecs', 'barn-megaparsec'], lambda v: v * Decimal('324078')),
        (['Hubble-barn'], lambda v: v * Decimal('76.6')),
        (['acre-feet'], lambda v: v * Decimal('0.000810713194')),
    ],
    'velocity': [
        (['attoParsecs / microfortnight', 'attoparsec per microfortnight'], lambda v: v * Decimal('39.2004663')),
        (['smoots / nanocentury', 'smoot per nanocentury'], lambda v: v * Decimal('1.854')),
        (['light seconds / dog year', 'light-seconds per dog year'], lambda v: v * Decimal('0.01503')),
    ],
    'time': [
        (['microcenturies'], lambda t: t / Decimal('3155.69')),
        (['nanocenturies'], lambda t: t / Decimal('3.155')),
        (['microfortnights'], lambda t: t * Decimal('0.8267')),
        (['dog years'], lambda t: t / Decimal('4505160')),
    ],
    'power': [
        (['donkey power', 'brake donkey power'], lambda p: p / Decimal('4')),
    ],
}


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
        result = result[places-2:]
    elif value > 900000000:
        result = [' million'] + result[9+places:]
    else:
        result = result[places+1:]

    formatted = ''.join(reversed(result))
    if '.' in formatted:
        return formatted.rstrip('0')
    return formatted

def convert_useless(category, value):
    if category not in USELESS_UNITS.keys():
        return None
    units, convert = random.choice(USELESS_UNITS[category])
    unit = random.choice(units)
    converted = convert(value)
    if category != 'mass' and converted < 0.1:
        return None
    return '%s %s' % (prettify(converted), unit)


TESTS = [
    # length
    u'AT closest approach, the New Horozon probe was 7,800 miles from Pluto.',  # noqa
    u'Just to clear this up: Sophie is 5\'9" plus heels; Gwendoline is 6\'3" plus heels (flaunt it girl!); Kit is 5\'8" plus no heels. 5\'8" isn\'t exactly tall, but it\'s not as bad as this photo makes it appear.',  # noqa
    # mass
    u'Your momma so fat she weight 300 pounds!',
    # volume
    u'Over 25,000 gallons of water were used to make the meat in those burgers.',  # noqa
    u'That is 1500 ounces (44.36 liters) for him and 750 ounces (22.18 liters) for her.',  # noqa
    # velocity
    u'So it would be like taking a picture of something a mile away from a car travelling at 15 miles per hour.',  # noqa
    # time
    u'that was 3 weeks ago, lets check again in 15 minutes',
    # power
    u'this car makes 350 bhp, that\'s almost 220 kW!',
]

if __name__ == '__main__':
    for i, test in enumerate(TESTS):
        print 'Test #%02d' % i
        print '"%.50s"' % test
        for value, info in get_units(test).items():
            print 'value: %s from %s' % (value, info['original'])
            print convert_useless(info['category'], value)
        print ''
