import CommonMark
import pprint

import logging
logger = logging.getLogger('consolemd')

class ConsoleMD(object):

    def __init__(self, parser, formatter, style):
        if parser is None:
            parser = CommonMark.Parser()

        self.parser    = parser
        self.formatter = formatter
        self.style     = style
        self.prefix    = []
        self.list_level= -1
        self.counters  = {}

    def render(self, fout, md):
        ast = self.parser.parse( md )

        for obj, entering in ast.walker():
            # print obj, entering
            # continue
            style_out = getattr(self.style, obj.t)(obj, entering)
            fout.write(style_out)

            out = self._dispatch(obj, entering)
            if out is not None:
                fout.write(out)

    def _dispatch(self, obj, entering):
        try:
            handler = getattr(self, '_' + obj.t)
            return handler(obj, entering)
        except KeyError:
            logger.error( "unhandled ast type: {}\n".format(obj.t) )

        return None

    def _ignore(self, obj, entering):
        return None

    def _document(self, obj, entering):
        if entering:
            self.prefix.append('')
        else:
            self.prefix.pop()

        return ''

    def _paragraph(self, obj, entering):
        #pprint.pprint(obj.__dict__)
        if entering:
            if obj.prv and obj.prv.t == 'paragraph':
                return '\n'
            else:
                return ''
        else:
            return '\n'

    def _text(self, obj, entering):
        return self.prefix[-1] + obj.literal

    def _softbreak(self, obj, entering):
        return ' '

    def _emph(self, obj, entering):
        return ''

    def _strong(self, obj, entering):
        return ''

    def _heading(self, obj, entering):
        if entering:
            prefix = '' if obj.prv is None else '\n'
            level = 1 if obj.level is None else obj.level
            return prefix + '#'*level + ' '
        else:
            return '\n'

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
            #pprint.pprint(obj.__dict__)
            return '\n'
        return ''

    def _item(self, obj, entering):
        # TODO a counter if numbered list
        # item.list_data.type is [bullet, ordered]
        if entering:
            if obj.list_data['type'] == 'ordered':
                key = tuple(obj.parent.sourcepos[0])
                self.counters[key] += 1
                num = self.counters[key]
                bullet_char = "{}.".format(num)
            else:
                bullet_char = obj.list_data.get('bullet_char') or '*' # -,+,*

            return ' '*self.list_level*2 + bullet_char + ' '

        return ''

    def _code(self, obj, entering):
        # backticks
        return obj.literal

    def _code_block(self, obj, entering):
        # TODO pass obj.literal to pygments
        if entering and obj.prv and obj.prv.t == 'paragraph':
            prefix = '\n'
        else:
            prefix = ''

        return prefix + obj.literal + '\n'

    def _block_quote(self, obj, entering):
        if entering:
            #pprint.pprint(obj.__dict__)
            self.prefix.append('> ')

            if obj.prv and obj.prv.t == 'paragraph':
                return '\n'
            else:
                return ''
        else:
            self.prefix.pop()
            return '\n'

    def _link(self, obj, entering):
        # THINK underline?
        if entering:
            return '['
        else:
            return "]({})".format(obj.destination)

    def _image(self, obj, entering):
        # THINK underline?
        if entering:
            return '['
        else:
            return "]({})".format(obj.destination)



