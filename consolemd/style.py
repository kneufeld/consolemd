# -*- coding: utf-8 -*-

from .terminal256 import EscapeSequence

class Style(object):
    def __init__(self):
        self.stack = []

    def __getattr__(self, name):
        def _ignore(obj, entering):
            return ''
        return _ignore

    def push(self, eseq):
        self.stack.append(eseq)
        return eseq

    def pop(self):
        return self.stack.pop()

    @staticmethod
    def to_rgb(color):
        if color[0] == '#':
            color = color[1:]

        color = int(color, 16)

        r = (color >> 16) & 0xff
        g = (color >> 8) & 0xff
        b = color & 0xff

        return r,g,b

    @staticmethod
    def from_rgb(r,g,b):
        # hex() produces "0x88", we want just "88"
        return "#" + "".join([hex(i)[2:] for i in [r,g,b]])

    @staticmethod
    def reshade( color, per):
        if per == 1.0:
            return color

        r,g,b = Style.to_rgb(color)
        r,g,b = map( lambda c: int(c*per), [r,g,b] )
        return Style.from_rgb(r,g,b)

class NativeStyle(Style):

    def document(self, obj, entering):
        if entering:
            return ''
        else:
            return EscapeSequence().reset_string()

    def thematic_break(self, obj, entering):
        return EscapeSequence().reset_string()

    def emph(self, obj, entering):
        if entering:
            return self.push(EscapeSequence(italic=True)).color_string()
        else:
            return self.pop().reset_string()

    def strong(self, obj, entering):
        if entering:
            return self.push(EscapeSequence(bold=True)).color_string()
        else:
            return self.pop().reset_string()

    def heading(self, obj, entering):
        # make each heading level a bit darker
        orange =  "#cb4b16"
        if entering:
            level = 1 if obj.level is None else obj.level
            per = 1.0 - .05 * (level-1)
            color = Style.reshade(orange, per)
            eseq = EscapeSequence(fg=color, bold=True)
            return self.push(eseq).color_string()
        else:
            return self.pop().reset_string()

    def code(self, obj, entering):
        if entering:
            color = '#af8700'
            eseq = EscapeSequence(fg=color)
            return self.push(eseq).color_string()
        else:
            assert False, "this shouldn't be called, ConsoleMD() is resetting this token"

    def code_block(self, obj, entering):
        if entering:
            color = '#00afaf'
            eseq = EscapeSequence(fg=color, bold=True)
            return self.push(eseq).color_string()
        else:
            assert False, "this shouldn't be called, ConsoleMD() is resetting this token"

    def block_quote(self, obj, entering):
        if entering:
            return self.push(EscapeSequence(italic=True)).color_string()
        else:
            return self.pop().reset_string()

    def bullet(self, bullet):
        """
        this is not an official markdown type, but it's how we colorize
        just the bullet/number of a list item
        """
        eseq = EscapeSequence(fg='#268bd2', bold=True)
        return "{}{}{}".format(eseq.color_string(), bullet, eseq.reset_string())
