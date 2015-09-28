#!/usr/bin/env python
import re
from decimal import Decimal


r = lambda exp: re.compile(exp)


BLACKLIST = [
    '1000 yard stare',
    '8 mile',
    '2 feet',
    # '###any other bot'
]

RE_NUM = r"(\d+[\d ,'\.]+)"

UNITS = [
    # normalize to meter
    ('length', [
        (r(RE_NUM + r'(?:m| meters?|metres?)'), lambda m: m),
        (r(RE_NUM + r'(?:km| kilometers?|kilometres?)'), lambda km: km * 1000),
        (r(RE_NUM + r' ?in(?:ches?)?'), lambda i: i * Decimal('0.0254')),
        (r(RE_NUM + r' ?mi(?:les?)?(?! per)'), lambda mi: mi * Decimal('1609.34')),
        (r(RE_NUM + r' (?:yards?|yd)'), lambda y: y * Decimal('0.9144')),
        (r(RE_NUM + r' ?(?:feet|ft)'), lambda ft: ft * Decimal('0.3048')),
        (r(r'(\d)\'(\d{,2})"'),
            lambda ft, i: ft * Decimal('0.3048') + i * Decimal('0.0254')),
    ]),
    # normalize to kilogram
    ('mass', [
        (r(RE_NUM + r'(?:kg| kilogram[m|s]?)'), lambda kg: kg),
        (r(RE_NUM + r' ?(?:lb|pounds?)'), lambda lb: lb * Decimal('0.453592')),
    ]),
    # normalize to cubic meter
    ('volume', [
        (r(RE_NUM + r' ?(?:m3|m³)'), lambda m3: m3),
        (r(RE_NUM + r'(?:l| liters?|litres?)'), lambda l: l * Decimal('0.001')),
        (r(RE_NUM + r' ?(?:oz\.?|fl\.? ?oz\.?|ounces?|fl\.? ?ounces?|fluid ?oz\.?|fluid ?ounces?)'),  # noqa
            lambda oz: oz * Decimal('0.0000295735')),
        (r(RE_NUM + r' ?gallons?'), lambda g: g * Decimal('0.00378541')),
    ]),
    # normalize to meters per second
    ('velocity', [
        (r(RE_NUM + r' ?(?:m/s)'), lambda ms: ms),
        (r(RE_NUM + r' ?(?:miles per hour|mph)'),
            lambda mph: mph * Decimal('0.44704')),
    ]),
    # normalize to kelvin
    ('temperature', [
        # TODO
    ]),
    # normalize to seconds
    ('time', [
        # TODO
    ]),
]


def get_units(text):
    """
    Get mentioned units and quantities from a comment body.

    """
    values = {}
    text = text.lower()
    for type, units in UNITS:
        for r, normalize in units:
            matches = list(r.finditer(text))
            for match in matches:
                # overwrite latter occurences with higher precedence
                # (mph over just miles)
                if match.group(0).lower() in BLACKLIST:
                    continue
                groups = map(lambda s: Decimal(s.replace(',', '')
                                                .replace(' ', '')
                                                .replace("'", '')),
                             match.groups())
                values[normalize(*groups)] = type
    return values


TESTS = [
    u'Over 25,000 gallons of water were used to make the meat in those burgers.',  # noqa
    u'AT closest approach, the New Horozon probe was 7,800 miles from Pluto. So it would be like taking a picture of something a mile away from a car travelling at 5 miles per hour.',  # noqa
    u'why are dildos so damn big? iv average vagina depth is like 6 inches.....those things are fucking baby arms....',  # noqa
    u'That is 1500 ounces (44.36 liters) for him and 750 ounces (22.18 liters) for her.',  # noqa
    u'Just to clear this up: Sophie is 5\'9" plus heels; Gwendoline is 6\'3" plus heels (flaunt it girl!); Kit is 5\'8" plus no heels. 5\'8" isn\'t exactly tall, but it\'s not as bad as this photo makes it appear.',  # noqa
    u'He\'s like 7 feet tall!',
    u'I liked 8 mile, you know, the movie. This is a long 10 000 mile bridge',
    u'everybody is crying about the m4\'s... who cares when the game feels fucking horrible after the patch. people sliding accross the map at 100mph.',  # noqa
]

if __name__ == '__main__':
    for i, test in enumerate(TESTS):
        print 'Test %d: %r' % (i, get_units(test))
