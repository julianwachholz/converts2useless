#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import json
import sys

from useless import get_units, convert_useless

from convert_bot import ConvertBot


logger = logging.getLogger('main')


CAPS_SUBS = [  # reply ALL CAPS in these subreddits
    'totallynotrobots',
]



# SUBMISSIONS = collections.Counter()


REPLY_TEXTS = [
    u'{original}? that\'s like {value}!',
    u'{original} you say? that is like {value}. \\*the more you know\\*',
    u'in other words, {original} is exactly {value}. neat!',
    u'BTW, {original} is precisely {value}.',
    u'{original} damn! That is {value}!',
    u'I have calculated {original} as exactly.. {value}.',
    u'you can also say that\'s {value} instead of {original}',
    u'{value} is the same as {original}',
]
REPLY_INFO = u' ^[[BotInfo]](/r/Converts2Useless)'


def reply_comment(comment):
    """
    Check the comment for anything convert-worthy.

    Returns True if a reply has been posted.

    """
    units = get_units(comment.body)
    if not len(units):
        return False

    value = random.choice(units.keys())
    info = units[value]
    logger.debug('comment: %s -- "%.50s"..' % (comment.id, comment.body))
    logger.debug('found value: %r %r' % (value, info))

    useless = convert_useless(info['category'], value)
    if useless is None:
        return False

    submission = r.get_info(thing_id=comment.link_id)
    if submission.score < 1:
        return False

    if not _check_comment_score(comment):
        return False

    reply = random.choice(REPLY_TEXTS).format(original=info['original'], value=useless)
    logger.info('REPLY: %s' % reply)
    reply += REPLY_INFO
    if comment.subreddit.display_name in CAPS_SUBS:
        reply = reply.upper()

    try:
        comment.reply(reply)
        SUBMISSIONS[comment.link_id] += 1
        time.sleep(WAIT_AFTER)
    except praw.errors.RateLimitExceeded as e:
        logger.warn('RateLimitExceeded, sleeping %d seconds' % e.sleep_time)
        time.sleep(e.sleep_time)
        if e.sleep_time > 300:
            return True
        return reply_comment(comment)
    return True


def get_reddit():
    global r
    logger.info('Authenticating with Reddit.')
    r.set_oauth_app_info(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         redirect_uri=REDIRECT_URI)
    # r.set_access_credentials(**ACCESS_INFO)

    # url = r.get_authorize_url('uniqueKey', SCOPE, True)
    # access_info = r.get_access_information('***REMOVED***')


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
    global r
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
        write_lists(blacklist, whitelist)
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
