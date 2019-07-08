import sys
import re
import textwrap

import commonmark
import pygments
import pygments.lexers
import pygments.styles
import pygments.formatters

from .styler import Styler, Style
from .escapeseq import EscapeSequence, _true_color

import logging
logger = logging.getLogger('consolemd')

endl = '\n'


def debug_tag(obj, entering, match):
    if entering != match:
        return ''

    if entering:
        return u"<{}>".format(obj.t)

    return u"</{}>".format(obj.t)


class Renderer:

    def __init__(self, parser=None, style_name=None):

        if parser is None:
            parser = commonmark.Parser()

        if style_name is None:
            style_name = 'native'

        self.parser     = parser
        self.style_name = style_name
        self.list_level = -1
        self.counters   = {}
        self.footnotes  = []

    def render(self, text, **kw):
        stream              = kw.get('output', sys.stdout)
        self.width          = kw.get('width', None)
        self.soft_wrap      = kw.get('soft_wrap', True)
        self.soft_wrap_char = endl if self.soft_wrap else ' '

        text = self.wrap_paragraphs(text)

        self.styler = Styler(stream, self.style_name)
        ast = self.parser.parse(text)

        for obj, entering in ast.walker():
            with self.styler.cm(obj, entering):
                prefix = self.prefix(obj, entering)
                stream.write(prefix)

                logger.debug(debug_tag(obj, entering, True))

                out = self.dispatch(obj, entering)
                stream.write(out)

                logger.debug(debug_tag(obj, entering, False))

                stream.flush()

    def dispatch(self, obj, entering):
        try:
            handler = getattr(self, obj.t)
            out = handler(obj, entering)
            return out
        except AttributeError:
            logger.error(u"unhandled ast type: {}".format(obj.t))

        return ''

    def wrap_paragraphs(self, text):
        """
        unfortunately textwrap expects to work on paragraphs, not entire
        documents. If the user has specified a width then we need to wrap
        the paragraphs individually before we parse the document.
        """
        if not self.width:
            return text

        para_edge = re.compile(r"(\n\s*\n)", re.MULTILINE)
        paragraphs = para_edge.split(text)

        wrapped_lines = []
        for para in paragraphs:
            wrapped_lines.append(
                textwrap.fill(para, width=self.width)
            )

        return '\n'.join(wrapped_lines)

    def prefix(self, obj, entering):
        """
        having newlines before text blocks is problematic, this function
        tries to catch those corner cases
        """
        if not entering:
            return ''

        if obj.t == 'document':
            return ''

        # if our parent is the document the prefix a newline
        if obj.parent.t == 'document':
            # don't prefix the very first one though
            if obj.parent.first_child != obj:
                return endl

        return ''

    def document(self, obj, entering):
        if entering:
            return ''
        else:
            formatted_footnotes = []
            for i, footnote in enumerate(self.footnotes):
                i += 1

                f = u"[{}] - {}".format(i, footnote)
                formatted_footnotes.append(f)

            if formatted_footnotes:
                return endl + endl.join(formatted_footnotes) + endl

            return ''

    def paragraph(self, obj, entering):
        if entering:
            return ''
        else:
            return endl

    def text(self, obj, entering):
        return obj.literal

    def linebreak(self, obj, entering):
        return endl

    def softbreak(self, obj, entering):
        return self.soft_wrap_char

    def thematic_break(self, obj, entering):
        width = self.width if self.width else 75
        return u"{}".format('—' * width) + endl

    def emph(self, obj, entering):
        return ''

    def strong(self, obj, entering):
        return ''

    def heading(self, obj, entering):
        if entering:
            level = 1 if obj.level is None else obj.level
            return u"{} ".format('#' * level)
        else:
            return endl

    def list(self, obj, entering):
        if entering:
            self.list_level += 1
        else:
            self.list_level -= 1

        if obj.list_data['type'] == 'ordered':
            if entering:
                # item nodes will increment this
                start = obj.list_data['start'] - 1
                self.counters[ tuple(obj.sourcepos[0]) ] = start
            else:
                del self.counters[ tuple(obj.sourcepos[0]) ]

        return ''

    def item(self, obj, entering):
        if entering:
            if obj.list_data['type'] == 'ordered':
                key = tuple(obj.parent.sourcepos[0])
                self.counters[key] += 1
                num = self.counters[key]
                bullet_char = u"{}.".format(num)
            else:
                bullet_char = obj.list_data.get('bullet_char') or '*' # -,+,*

            text = u"{}{} ".format(' ' * self.list_level * 2, bullet_char)
            eseq = self.styler.style.entering('bullet')

            return self.styler.stylize(eseq, text)

        return ''

    def code(self, obj, entering):
        # backticks
        return obj.literal

    def code_block(self, obj, entering):
        # farm out code highlighting to pygments
        # note: unfortunately you can't set your own background color
        # because after the first token the color codes would get reset

        try:
            lang  = obj.info or 'text'
            lexer = pygments.lexers.get_lexer_by_name(lang)
            style = Style.get_style_by_name(self.style_name)
        except pygments.util.ClassNotFound: # lang is unknown to pygments
            lang  = 'text'
            lexer = pygments.lexers.get_lexer_by_name(lang)
            style = Style.get_style_by_name(self.style_name)

        formatter_name = 'console16m' if _true_color else 'console'
        formatter = pygments.formatters.get_formatter_by_name(formatter_name, style=style)

        highlighted = u"{}{}".format(
            pygments.highlight(obj.literal.encode('utf-8'), lexer, formatter).rstrip(),
            EscapeSequence.full_reset_string() + endl,
        )
        eseq = EscapeSequence(bg="#202020")

        return self.styler.stylize(eseq, highlighted)

    def block_quote(self, obj, entering):
        # has text children
        return ''

    def link(self, obj, entering):
        if entering:
            self.footnotes.append(obj.destination)
            return ''
        else:
            return u"[{}]".format(len(self.footnotes))

    def image(self, obj, entering):
        if entering:
            self.footnotes.append(obj.destination)
            return '<image:'
        else:
            return u">[{}]".format(len(self.footnotes))

    def html_inline(self, obj, entering):
        if obj.literal.lower() in ['<br>', '<br/>']:
            return endl

        return obj.literal

    def html_block(self, obj, entering):
        logger.warning("ignoring html_block")
        return ''

        renderer = Renderer(self.parser, self.style_name)
        renderer.render(obj.literal[4:-3])
        return ''
