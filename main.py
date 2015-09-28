#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import collections
import logging
import random
import time

from datetime import datetime, timedelta
from itertools import cycle

import praw

from useless import get_units, convert_useless


FORMAT = '%(asctime)-15s %(levelname)-8s %(name)-10.10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('converts2useless')


USER_AGENT = 'Converts2Useless v1.1.1 (by /u/yousai)'

CLIENT_ID = '***REMOVED***'
CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

SCOPE = 'identity read submit edit privatemessages'

BOT_NAME = 'Converts2Useless'

ACCESS_INFO = {
    'access_token': '***REMOVED***',
    'scope': set(SCOPE.split()),
    'refresh_token': '***REMOVED***',
}

r = praw.Reddit(user_agent=USER_AGENT)


LIMIT = 50
MAX_AGE = timedelta(minutes=15)
MAX_DEPTH_CHECK = 4  # check scores on X parent comments
WAIT_AFTER = 60  # how long to wait after posting a comment

SUBMISSIONS = collections.Counter()


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


def check_comment(comment, blacklist):
    now = datetime.utcnow()
    created = datetime.utcfromtimestamp(comment.created_utc)

    if SUBMISSIONS[comment.link_id] > 3:
        logger.info('submission cap on thread %s reached' % comment.submission.fullname)
        return False

    if created + MAX_AGE < now:
        logger.debug('%s is older than 15min (now: %s)' % (created, now))
        return False

    if comment.author.name in blacklist:
        logger.info('/u/%s is on blacklist' % comment.author.name)
        return False
    return True

def _check_comment_score(comment, depth=0):
    """Check if any parent comment has a negative score."""
    if comment.author.name == BOT_NAME:
        return False  # dont participate in reply chains
    if not comment.score_hidden and comment.score < 1:
        return False
    if comment.is_root or depth > MAX_DEPTH_CHECK:
        return True
    global r
    logger.info('checking score on %s: depth %d' % (comment.parent_id, depth))
    parent = r.get_info(thing_id=comment.parent_id)
    return _check_comment_score(parent, depth + 1)


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
    try:
        comment.reply(reply + REPLY_INFO)
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
    r.set_access_credentials(**ACCESS_INFO)

    # url = r.get_authorize_url('uniqueKey', SCOPE, True)
    # access_info = r.get_access_information('***REMOVED***')
    logger.info('Logged in as %s (%s)' % (r.user.name, r.user.id))


def get_comments(sub, blacklist, before=None):
    """
    Always remember ID of last submitted comment, so we don't
    have to save anything else to keep running and not do the
    same work twice.

    """
    logger.debug('newest %d comments from /r/%s after %r'
                % (LIMIT, sub.display_name, before))
    latest_created = 0
    params = {
        'before': before,
        'sort': 'old',
    }
    for comment in sub.get_comments(limit=LIMIT, params=params):
        if comment.created_utc > latest_created:
            latest_created = comment.created_utc
            before = comment.fullname
        if check_comment(comment, blacklist) and reply_comment(comment):
            return comment.fullname
    return before


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


def read_lists():
    with open('blacklist.txt') as f:
        blacklist = set(map(lambda s: s.strip(), f.readlines()))
        logger.info('updated blacklist: %d entries' % len(blacklist))
    with open('whitelist.txt') as f:
        subreddits = set(map(lambda s: s.strip(), f.readlines()))
        logger.info('updated whitelist: %d entries' % len(subreddits))
    return blacklist, subreddits


def write_lists(blacklist, whitelist):
    with open('blacklist.txt', 'w') as f:
        f.write('\n'.join(blacklist))
    with open('whitelist.txt', 'w') as f:
        f.write('\n'.join(whitelist))


def loop(blacklist, subs):
    global r
    last_fullnames = {}

    logger.info('looping %r' % subs)

    try:
        for sub_name in cycle(subs):
            logger.debug('cycle: %s' % sub_name)
            latest = last_fullnames.get(sub_name, None)
            last_fullnames[sub_name] = get_comments(r.get_subreddit(sub_name), blacklist, before=latest)
            if check_mail(blacklist, subs):
                break
            time.sleep(2)
    except praw.errors.Forbidden:
        # bot got a 403 when trying to reply, remove subreddit from whitelist
        logger.error('Forbidden in /r/%s' % sub_name)
        subs.remove(sub_name)
        write_lists(blacklist, subs)


def main():
    get_reddit()

    while True:
        # loop only breaks if subreddits needs updating
        blacklist, subreddits = read_lists()
        loop(blacklist, subreddits)
        logger.info('loop refreshed')


if __name__ == '__main__':
    main()
