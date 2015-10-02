#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import json
import sys

from convert_bot import ConvertBot


logger = logging.getLogger('main')


START_TEXT = u'hey %s! you are now whitelisted for me! yay!'
STOP_TEXT = u'hey %s, you are now blacklisted and won\'t be bothered by me anymore.'


def _reply_mail(message, recipient, stop=False):
    if stop:
        text = STOP_TEXT % recipient
    else:
        text = START_TEXT % recipient
    message.mark_as_read()
    message.reply(text)


def check_mail(blacklist, whitelist):
    """Returns True if SUBREDDITS changed."""
    r = None
    if not r.get_me().has_mail:
        logger.debug('no new mails')
        return False
    messages = list(r.get_unread(unset_has_mail=True))
    logger.info('has %d mails' % len(messages))

    updated = False

    for message in messages:
        if 'start' in message.subject.lower():
            if message.author is None and message.subreddit:
                if message.subreddit.display_name not in whitelist:
                    logger.info('start /r/%s' % message.subreddit.display_name)
                    whitelist.add(message.subreddit.display_name)
                    _reply_mail(message, '/r/' + message.subreddit.display_name)
                    updated = True
            elif message.author.name in blacklist:
                logger.info('start /u/%s' % message.author.name)
                blacklist.remove(message.author.name)
                _reply_mail(message, '/u/' + message.author.name)
                updated = True
        elif 'stop' in message.subject.lower():
            if message.author is None and message.subreddit:
                if message.subreddit.display_name in whitelist:
                    logger.info('stop /r/%s' % message.subreddit.display_name)
                    whitelist.remove(message.subreddit.display_name)
                    _reply_mail(message, '/r/' + message.subreddit.display_name, stop=True)
                    updated = True
            elif message.author and message.author.name not in blacklist:
                logger.info('stop /u/%s' % message.author.name)
                blacklist.add(message.author.name)
                _reply_mail(message, '/u/' + message.author.name, stop=True)
                updated = True

    if updated:
        # write_lists(blacklist, whitelist)
        return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} <config_file>'.format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1]) as config_file:
        config = json.load(config_file)

    LOG_FORMAT = '%(asctime)-15s %(levelname)-6s %(name)-15.15s %(message)s'
    logging.basicConfig(level=config.get('loglevel', 'WARN'), format=LOG_FORMAT)

    bot = ConvertBot(config)
    bot.start()
