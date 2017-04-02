# -*- coding: utf-8 -*-

import pygments.styles
import pygments.lexers
import pygments.formatters
from pygments import token

from .escapeseq import EscapeSequence
from .colormap import reshade

import logging
logger = logging.getLogger('consolemd.styler')

# based on solarized dark
solarized = {
    'text':         '',
    'heading':      '#cb4b16 bold', # orange
    'emph':         'italic',
    'strong':       'bold',
    'block_quote':  'italic',
    'code':         '#af8700', # yellow
    'link':         '#0087ff',
    'image':        '#0087ff',
    'bullet':       '#268bd2 bold', # blue
    }

class Style(object):

    def __init__(self, style_name):
        self.pyg_style = pygments.styles.get_style_by_name(style_name)

        f = self.eseq_from_pygments # shortcut

        # each style has an entering value and an exiting value, None means reset
        self.styles = {
            'heading':      (f(token.Generic.Heading , solarized['heading'])     , None) ,
            'emph':         (f(token.Generic.Emph    , solarized['emph'])        , None) ,
            'strong':       (f(token.Generic.Strong  , solarized['strong'])      , None) ,
            'link':         (f(token.Name.Entity     , solarized['link'])        , None) ,
            'image':        (f(token.Name.Entity     , solarized['image'])       , None) ,
            'code':         (f(token.String.Backtick , solarized['code'])        , None) ,
            'block_quote':  (f(token.Generic.Emph    , solarized['block_quote']) , None) ,
            'bullet':       (f(token.Literal         , solarized['bullet'])      , None) ,
                }

        #print self.styles

    def eseq_from_pygments(self, token, default=''):
        value = self.pyg_style.styles.get(token, '') or default
        values = value.split()

        def fg(values):
            try:
                return filter(lambda val: val.startswith('#'), values)[0]
            except IndexError:
                return ''

        def bg(values):
            try:
                bg = filter(lambda val: val.startswith('bg:'), values)[0]
                return bg.split('bg:')[1]
            except IndexError:
                return ''

        return EscapeSequence(
                fg        = fg(values),
                bg        = bg(values),
                bold      = 'bold' in values,
                underline = 'underline' in values,
                italic    = 'italic' in values,
                )

    def entering(self, key):
        return self.styles.get(key, (None,None))[0] or EscapeSequence()

    def exiting(self, key):
        return self.styles.get(key, (None,None))[1] or self.entering(key)


class Styler(object):

    no_closing_node = [
            'text', 'code', 'code_block',
            'thematic_break', 'softbreak', 'linebreak',
            ]

    def __init__(self, stream, style_name):

        self.stream = stream
        self.style_name = style_name
        self.style = Style(style_name)

        self.stack = []

    def cm(self, obj, entering):
        self._curr_call = (obj, entering)
        return self

    def __enter__(self):
        obj, entering = self._curr_call

        if entering:
            eseq = self.dispatch( obj, entering )
            self.push( eseq )
            self.stream.write( eseq.color_string() )

    def __exit__(self, exc_type, exc_value, traceback):
        obj, entering = self._curr_call
        # import pprint
        # print entering, obj.t, pprint.pformat(obj.__dict__)

        if not entering or obj.t in Styler.no_closing_node:
            eseq = self.stack.pop()
            self.stream.write( eseq.reset_string() )

            if obj.t != 'document':
                eseq = self.stack[-1]
                self.stream.write( eseq.color_string() )

    def __getattr__(self, name):
        from functools import partial
        return partial(self._default, name)

    def push(self, eseq):
        self.stack.append(eseq)
        return eseq

    def pop(self):
        return self.stack.pop()

    @staticmethod
    def stylize( eseq, text ):
        return "{}{}{}".format(eseq.color_string(), text, eseq.reset_string())

    def dispatch(self, obj, entering):
        """
        returns an EscapeSequence object
        """
        try:
            handler = getattr(self, obj.t)
            return handler(obj, entering)
        except KeyError:
            logger.error( "unhandled ast type: {}".format(obj.t) )

        return ''

    def _default(self, name, obj, entering):
        if entering:
            return self.style.entering(name)
        else:
            return self.style.exiting(name)

    def heading(self, obj, entering):
        # make each heading level a bit darker
        eseq = self.style.entering('heading')
        color = eseq.fg

        level = 1 if obj.level is None else obj.level
        per = 1.0 - .05 * (level-1)
        eseq.fg = reshade(color, per)
        return eseq

    def code(self, obj, entering):
        eseq = self.style.entering('code')
        return eseq

    def bullet(self, obj, entering):
        """
        this is not an official markdown type, but it's how we colorize
        just the bullet/number of a list item
        """
        eseq = self.style.entering('bullet')
        eseq.stream = self.stream
        return eseq
