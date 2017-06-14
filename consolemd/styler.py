# -*- coding: utf-8 -*-

import copy

import pygments.styles
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

    plain = EscapeSequence()

    def __init__(self, style_name):
        self.pyg_style = Style.get_style_by_name(style_name)

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

    @staticmethod
    def get_style_by_name(style_name):
        try:
            return pygments.styles.get_style_by_name(style_name)
        except pygments.util.ClassNotFound:
            logger.error("no such style: %s", style_name)
            return pygments.styles.get_style_by_name('native')

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
        return self.styles.get(key, (None,None))[0] or Style.plain

    def exiting(self, key):
        return self.styles.get(key, (None,None))[1] or self.entering(key)


class Styler(object):

    no_closing_node = [
            'text', 'code', 'code_block',
            'thematic_break', 'softbreak', 'linebreak',
            'html_inline', 'html_block',
            ]

    def __init__(self, stream, style_name):

        self.stream = stream
        self.style_name = style_name
        self.style = Style(style_name)

        self._stack = []
        self._curr_call = None

    def cm(self, obj, entering):
        """
        return ourselves as a context manager, unfortunately __enter__
        can't take any parameters
        """
        assert self._curr_call == None, "Styler is not re-entrant"
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
        self._curr_call = None

        if not entering or obj.t in Styler.no_closing_node:
            eseq = self._stack.pop()
            self.stream.write( eseq.reset_string() )

            if obj.t != 'document':
                eseq = self._stack[-1]
                self.stream.write( eseq.color_string() )
            else:
                assert len(self._stack) == 0, "missed an ast type in no_closing_node"

    def __getattr__(self, name):
        from functools import partial
        return partial(self._default, name)

    @staticmethod
    def stylize( eseq, text ):
        return u"{}{}{}".format(eseq.color_string(), text, eseq.reset_string())

    def _default(self, name, obj, entering):
        """
        __getattr__ returns this function if a specific/overriding method
        is not provided in this class
        """
        if entering:
            return self.style.entering(name)
        else:
            return self.style.exiting(name)

    def push(self, eseq):
        self._stack.append(eseq)
        return eseq

    def pop(self):
        return self._stack.pop()

    def dispatch(self, obj, entering):
        """
        returns an EscapeSequence object
        """
        handler = getattr(self, obj.t)
        return handler(obj, entering)

    def heading(self, obj, entering):
        """
        do specialized styling for headers, make each heading level a bit darker
        """
        eseq = copy.deepcopy( self.style.entering('heading') )
        color = eseq.fg

        level = 1 if obj.level is None else obj.level
        per = 1.0 - .10 * (level-1)
        eseq.fg = reshade(color, per)

        return eseq
