# -*- coding: utf-8 -*-

import CommonMark
import pprint

from .style import NativeStyle

import logging
logger = logging.getLogger('consolemd')

class ConsoleMD(object):

    def __init__(self, parser, style=None):
        if parser is None:
            parser = CommonMark.Parser()

        if style is None:
            style = NativeStyle()

        if type(style) is str:
            import pygments.styles
            style = pygments.styles.get_style_by_name(style)

        # class MonkeyStyle(style):
        #     styles = dict( style.styles.items() + { Generic.Search:'#ff00f0' }.items() )

        self.parser     = parser
        self.style      = style
        self.list_level = -1
        self.counters   = {}

    def render(self, fout, md):
        def debug_tag(obj, entering):
            if entering:
                return "<{}>".format(obj.t)
            return "</{}>".format(obj.t)

        ast = self.parser.parse( md )

        for obj, entering in ast.walker():
            # print obj, entering
            # continue
            style_out = getattr(self.style, obj.t)(obj, entering)
            fout.write(style_out)

            prefix = self._prefix(obj, entering)
            out = self._dispatch(obj, entering)

            if out is not None:
                fout.write(prefix)
                #print debug_tag(obj,entering),
                fout.write(out)

    def _dispatch(self, obj, entering):
        try:
            handler = getattr(self, '_' + obj.t)
            return handler(obj, entering)
        except KeyError:
            logger.error( "unhandled ast type: {}".format(obj.t) )
            logger.debug( "entering: %s,\n%s", entering, pprint.pformat(obj.__dict__) )

        return None

    def _prefix(self, obj, entering):
        if not entering    : return ''
        if obj.t == 'text' : return ''
        if not obj.prv     : return ''
        if obj.t == 'list' : return '' # this feels dirty but sublists get newlined otherwise

        if obj.prv.t == 'paragraph':
            return '\n'

        return ''

    def _ignore(self, obj, entering):
        return None

    def _document(self, obj, entering):
        return ''

    def _paragraph(self, obj, entering):
        #pprint.pprint(obj.__dict__)
        if entering:
            return ''
        else:
            return '\n'

    def _text(self, obj, entering):
        return obj.literal

    def _linebreak(self, obj, entering):
        return '\n'

    def _softbreak(self, obj, entering):
        return ' '

    def _thematic_break(self, obj, entering):
        # an "not entering" node is not generated
        return '-'*75 + '\n'

    def _emph(self, obj, entering):
        return ''

    def _strong(self, obj, entering):
        return ''

    def _heading(self, obj, entering):
        if entering:
            level = 1 if obj.level is None else obj.level
            return '#'*level + ' '
        else:
            return '\n\n'

    def _list(self, obj, entering):
        if entering:
            self.list_level += 1
        else:
            self.list_level -= 1

        if entering and obj.list_data['type'] == 'ordered':
            start = obj.list_data['start'] - 1
            self.counters[ tuple(obj.sourcepos[0]) ] = start

            # if obj.parent.t == 'item' and obj.parent.list_data['type'] == 'ordered':
            #     self.prefix.append( self.prefix[-1] + '1.' )
            # else:
            #     self.prefix.append('1.')

        if not entering and obj.list_data['type'] == 'ordered':
            del self.counters[ tuple(obj.sourcepos[0]) ]

        if entering:
            return ''
        elif obj.nxt is not None:
            # if we're not a nested list then newline
            return '\n'

        return ''

    def _item(self, obj, entering):
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

            return ' '*self.list_level*2 + self.style.bullet(bullet_char) + ' '

        return ''

    def _code(self, obj, entering):
        # backticks
        return obj.literal + self.style.pop().reset_string()

    def _code_block(self, obj, entering):
        # TODO pass obj.literal to pygments
        #pprint.pprint(obj.__dict__)
        #obj.info contains the language or '' if not provided
        return obj.literal + self.style.pop().reset_string() + '\n'

    def _block_quote(self, obj, entering):
        if entering:
            return ''
        else:
            return '\n'

    def _link(self, obj, entering):
        if entering:
            return '['
        else:
            return "]({})".format(obj.destination)

    def _image(self, obj, entering):
        if entering:
            return '!['
        else:
            return "]({})".format(obj.destination)



