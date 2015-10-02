# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import logging
from operator import attrgetter

from reddit_bot import RedditReplyBot, RedditMessageBot
from unit import Unit


logger = logging.getLogger(__name__)


class ConvertBot(RedditReplyBot, RedditMessageBot):

    def get_comment_checks(self):
        checks = super(ConvertBot, self).get_comment_checks()
        return checks + [self.comment_has_units]

    def comment_has_units(self, comment):
        logger.debug('comment_has_units(comment={!r})'.format(comment.id))
        return any(Unit.find_units(comment.body))

    def reply_comment(self, comment):
        units = Unit.find_units(comment.body)
        largest_unit = max(units, key=attrgetter('value'))

        logger.info('comment {!r} has units!'.format(comment.id))
        logger.info('largest value: {!r}'.format(largest_unit))
