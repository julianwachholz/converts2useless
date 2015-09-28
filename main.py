#!/usr/bin/env python
import logging
from datetime import datetime

from praw import Reddit

FORMAT = '%(asctime)-15s %(levelname)-8s %(name)-10.10s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger('converts2useless')


USER_AGENT = 'Converts2Useless v0.0 (by /u/yousai)'

CLIENT_ID = '***REMOVED***'
CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

SCOPE = 'identity read submit edit'

ACCESS_INFO = {
    'access_token': '***REMOVED***',
    'scope': set(SCOPE.split()),
    'refresh_token': '***REMOVED***',
}

SUBREDDITS = [
    'test',
]

LIMIT = 25


def check_comment(comment):
    """
    Check the comment for anything convert-worthy.

    """
    logger.debug('checking %r' % comment.fullname)
    units = get_units(comment.body)
    if units:
        comment.reply(u'That\'s pretty cool!')


def get_reddit():
    logger.info('Authenticating with Reddit.')
    r = Reddit(user_agent=USER_AGENT)
    r.set_oauth_app_info(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         redirect_uri=REDIRECT_URI)
    r.set_access_credentials(**ACCESS_INFO)

    # url = r.get_authorize_url('uniqueKey', SCOPE, True)
    # access_info = r.get_access_information('***REMOVED***')
    logger.info('Logged in as %s (%s)' % (r.user.name, r.user.id))
    return r


def get_comments(sub, before=None):
    """
    Always remember ID of last submitted comment, so we don't
    have to save anything else to keep running and not do the
    same work twice.

    """
    logger.info('newest %d comments from /r/%s after %r'
                % (LIMIT, sub.display_name, before))
    latest_created = 0
    params = {
        'before': before,
        'sort': 'old',
    }

    for comment in sub.get_comments(limit=LIMIT, params=params):
        check_comment(comment)

        if comment.created_utc > latest_created:
            latest_created = comment.created_utc
            before = comment.fullname
    else:
        logger.info('No new comments here.')
    return before


def main(latest_fullname=None):
    r = get_reddit()
    logger.debug('UTC time: %s', datetime.utcnow())

    # TODO make it loop over subs
    import time
    for sub_name in SUBREDDITS:
        while True:
            latest_fullname = get_comments(r.get_subreddit(sub_name),
                                           before=latest_fullname)
            time.sleep(10)


if __name__ == '__main__':
    import sys
    logger.debug('%r' % sys.argv)
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
