#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import json
import sys

from convert_bot import ConvertBot


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} <config_file>'.format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1]) as config_file:
        logger.debug('loaded config from {}'.format(sys.argv[1]))
        config = json.load(config_file)

    LOG_FORMAT = '%(asctime)-15s %(levelname)-6s %(name)-15.15s %(message)s'
    logging.basicConfig(level=config.get('loglevel', 'WARN'), format=LOG_FORMAT)

    bot = ConvertBot(config)
    bot.start()
