# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
from random import choice
from operator import attrgetter

from reddit_bot import RedditReplyBot, RedditMessageBot
from unit import Unit


logger = logging.getLogger(__name__)


def _template_choice(match):
    return choice(match.group(1).split('/'))


def compile_template(template):
    """Takes a substitution template and returns a function that takes format parameters."""
    reg = r'\[(.*?)\]'
    return lambda **kw: re.sub(reg, _template_choice, template).format(**kw)


REPLY_TEMPLATES = map(compile_template, [
    "{original}[/ you say]? [that is/that's] like {value}![ \\*the more you know\\*/]",
    "[In/in] other words, {original} is [exactly/precisely/specifically] {value}[,/.] [nice/neat/neato]!",
    "[BTW/btw,/Oh/oh,/Did you know?] {original} is [the same as/exactly/precisely/specifically] {value}[./!/]",
    "{original} [damn/wow/WOW]! [That/that][ is/'s] {value}[./!/]",
    "I have [calculated/computed/determined] {original} [as/is] [exactly/precisely/specifically] {value}[./!/]",
    "[You/you] [can/could] also say that[ is/'s] {value} [instead of/in place of/rather than] {original}[./!/]",
    "{value} is the same as {original}[, just so you know/][./!/]",
])

REPLY_INFO = ' [[BotInfo]](/r/Converts2Useless "Bot Version {}")'


# reply ALL CAPS in these subreddits
SUBREDDIT_MODIFIERS = {
    'totallynotrobots': str.upper,
}


class ConvertBot(RedditReplyBot, RedditMessageBot):

    VERSION = (1, 2, 0)

    def bot_start(self):
        super(ConvertBot, self).bot_start()
        self.reply_info = REPLY_INFO.format('.'.join(map(str, self.VERSION)))

    def get_comment_checks(self):
        checks = super(ConvertBot, self).get_comment_checks()
        return checks + [self.comment_has_units]

    def comment_has_units(self, comment):
        logger.debug('comment_has_units(comment={!r})'.format(comment.id))
        return any(Unit.find_units(comment.body))

    def reply_comment(self, comment):
        unit = max(Unit.find_units(comment.body), key=attrgetter('value'))

        logger.debug('comment {!r} has units!'.format(comment.id))
        logger.debug('largest value: {!r}'.format(unit))

        reply_text = choice(REPLY_TEMPLATES)(
            value=unit.to_useless(),
            original=unit.original
        )

        logger.info('reply_comment: {!r}'.format(reply_text))
        comment.reply(reply_text + self.reply_info)
        return True
