# -*- coding: utf-8 -*-

import CommonMark
import pprint
import pygments
import pygments.styles
import pygments.lexers
import pygments.formatters

from .styler import Styler
from .terminal256 import EscapeSequence

import logging
logger = logging.getLogger('consolemd')

class Renderer(object):

    def __init__(self, parser=None, style_name=None):
        if parser is None:
            parser = CommonMark.Parser()

        if style_name is None:
            style_name = 'native'

        # class MonkeyStyle(style):
        #     styles = dict( style.styles.items() + { Generic.Search:'#ff00f0' }.items() )

        self.parser     = parser
        self.style_name = style_name
        self.styler     = Styler(style_name)
        self.list_level = -1
        self.counters   = {}

    def render(self, fout, md):
        def debug_tag(obj, entering):
            if entering:
                return "<{}>".format(obj.t)
            return "</{}>".format(obj.t)

        ast = self.parser.parse( md )

        for obj, entering in ast.walker():
            prefix = self.prefix(obj, entering)
            fout.write(prefix)

            style_out = self.styler.dispatch(obj, entering)
            fout.write(style_out)

            out = self.dispatch(obj, entering)
            fout.write(out)

    def dispatch(self, obj, entering):
        try:
            handler = getattr(self, obj.t)
            return handler(obj, entering)
        except KeyError:
            logger.error( "unhandled ast type: {}".format(obj.t) )
            logger.debug( "entering: %s,\n%s", entering, pprint.pformat(obj.__dict__) )

        return None

    def prefix(self, obj, entering):
        """
        having newlines before text blocks is problematic, this function
        tries to catch those corner cases
        """
        if not entering    : return ''
        if obj.t == 'text' : return ''
        if not obj.prv     : return ''
        if obj.t == 'list' : return '' # this feels dirty but sublists get newlined otherwise

        if obj.prv.t == 'paragraph':
            return '\n'

        return ''

    def document(self, obj, entering):
        return ''

    def paragraph(self, obj, entering):
        if entering:
            return ''
        else:
            return '\n'

    def text(self, obj, entering):
        return obj.literal

    def linebreak(self, obj, entering):
        return '\n'

    def softbreak(self, obj, entering):
        return ' '

    def thematic_break(self, obj, entering):
        # an "not entering" node is not generated
        return '-'*75 + '\n'

    def emph(self, obj, entering):
        return ''

    def strong(self, obj, entering):
        return ''

    def heading(self, obj, entering):
        if entering:
            level = 1 if obj.level is None else obj.level
            return '#'*level + ' '
        else:
            return '\n\n'

    def list(self, obj, entering):
        if entering:
            self.list_level += 1
        else:
            self.list_level -= 1

        if entering and obj.list_data['type'] == 'ordered':
            start = obj.list_data['start'] - 1
            self.counters[ tuple(obj.sourcepos[0]) ] = start

        if not entering and obj.list_data['type'] == 'ordered':
            del self.counters[ tuple(obj.sourcepos[0]) ]

        if entering:
            return ''
        elif obj.nxt is not None:
            # if we're not a nested list then newline
            return '\n'

        return ''

    def item(self, obj, entering):
        # list item
        # obj.list_data.type is [bullet, ordered]
        if entering:
            if obj.list_data['type'] == 'ordered':
                key = tuple(obj.parent.sourcepos[0])
                self.counters[key] += 1
                num = self.counters[key]
                bullet_char = "{}.".format(num)
            else:
                bullet_char = obj.list_data.get('bullet_char') or '*' # -,+,*

            return ' '*self.list_level*2 + self.styler.bullet(bullet_char) + ' '

        return ''

    def code(self, obj, entering):
        # backticks
        return obj.literal + self.styler.pop().reset_string()

    def code_block(self, obj, entering):
        lang = obj.info or 'text'
        lexer = pygments.lexers.get_lexer_by_name(lang)
        style = pygments.styles.get_style_by_name(self.style_name)
        formatter = pygments.formatters.get_formatter_by_name('console16m', style=style)

        return pygments.highlight(obj.literal, lexer, formatter) \
                + EscapeSequence.full_reset_string() + '\n'

    def block_quote(self, obj, entering):
        if entering:
            return ''
        else:
            return '\n'

    def link(self, obj, entering):
        if entering:
            return '['
        else:
            return "]({})".format(obj.destination)

    def image(self, obj, entering):
        if entering:
            return '!['
        else:
            return "]({})".format(obj.destination)



