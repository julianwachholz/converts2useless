#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import logging
import json
import sys
import os

from praw import Reddit
from convert_bot import ConvertBot


logger = logging.getLogger(__name__)

LOG_FORMAT = '%(asctime)-15s %(levelname)-6s %(name)-15.15s %(message)s'
CONFIG_TEMPLATE = 'config.json.template'


def _ask_config(config, in_settings=False):
    for key, default in config.items():
        if key == 'settings':
            _ask_config(default, in_settings=True)
        elif isinstance(default, dict):
            _ask_config(default)
        elif in_settings or default.startswith('{') and default.endswith('}'):
            val_type = type(default)

            if isinstance(default, type('str')):
                default = default.strip('{}')

            if isinstance(default, type('str')) and default.isupper():
                while True:
                    value = raw_input("{}: ".format(key, default))
                    if value:
                        config[key] = value or default
                        break
                    else:
                        print "{} is required!".format(key)
            else:
                while True:
                    try:
                        value = raw_input("{} ({}): ".format(key, default))
                        if value:
                            value = val_type(value)
                        elif in_settings:
                            config.pop(key, None)
                            break
                    except ValueError as e:
                        print e
                    else:
                        config[key] = value or default
                        break


def make_config(filename):
    """
    Make a new config file.

    """
    here = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(here, CONFIG_TEMPLATE)

    with open(template_file, 'r') as f:
        config = json.load(f)

    print "Generating a new config, press [Enter] to accept default value."
    _ask_config(config)

    r = Reddit('praw/oauth_access_info_setup 1.0')
    r.set_oauth_app_info(**config['oauth_info'])

    url = r.get_authorize_url('uniqueKey', ConvertBot.get_scope(), True)
    print 'Go to this url: =====\n\n{}\n\n====='.format(url)
    code = raw_input('and enter the authorization code: ')
    assert code, "No authorization code supplied."
    access_info = r.get_access_information(code)
    access_info.pop('scope', None)
    config['access_info'] = access_info

    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)

    print "Wrote config '{}'!".format(filename)
    return config


def main(config_file):
    try:
        with open(sys.argv[1]) as config_file:
            logger.debug('loaded config from {}'.format(sys.argv[1]))
            config = json.load(config_file)
    except IOError:
        config = make_config(sys.argv[1])

    logging.basicConfig(level=config.get('loglevel', 'WARN'), format=LOG_FORMAT)

    if not os.path.exists(config['subreddit_list']):
        open(config['subreddit_list'], 'a').close()
        logger.info("Created empty {}".format(config['subreddit_list']))

    if not os.path.exists(config['blocked_users']):
        open(config['blocked_users'], 'a').close()
        logger.info("Created empty {}".format(config['blocked_users']))

    bot = ConvertBot(config)
    bot.start()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} <config_file>\n'.format(sys.argv[0]))
        sys.stderr.write('Will create <config_file> if it does not exist.\n')
        sys.exit(1)

    main(sys.argv[1])
