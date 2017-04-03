# -*- coding: utf-8 -*-

from consolemd.colormap import ColorMap, to_rgb, ansicolors

_true_color = True

class EscapeSequence(object):
    def __init__(self,
            fg=None, bg=None,
            bold=False, underline=False, italic=False, true_color=None,
            stream=None,
            ):

        self.fg        = fg
        self.bg        = bg
        self.bold      = bold
        self.underline = underline
        self.italic    = italic
        self.stream    = None

        if true_color is None:
            true_color = _true_color

        if true_color:
            self.color_string = self.true_color_string
        else:
            self.color_string = self.low_color_string

    def __str__(self):
        return self.color_string()

    def __repr__(self):
        return "<ESeq: {} {} {} {} {}>".format(
                self.fg or '_', self.bg or '_', self.bold, self.underline, self.italic
                )

    def __enter__(self):
        self.stream.write( self.color_string() )

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.write( self.reset_string() )

    @property
    def fg(self):
        return self._fg

    @fg.setter
    def fg(self, color):
        # convert incoming color to rgb string
        self._fg = ansicolors.get(color, color)

    @property
    def bg(self):
        return self._bg

    @bg.setter
    def bg(self, color):
        # convert incoming color to rgb string
        self._bg = ansicolors.get(color, color)

    def escape(self, attrs):
        if len(attrs):
            return "\x1b[" + ";".join(attrs) + "m"
        return ''

    def low_color_string(self):
        attrs = []

        if self.fg is not None:
            color = ColorMap( self.fg ).color
            attrs.extend(("38", "5", "%i" % color))

        if self.bg is not None:
            color = ColorMap( self.bg ).color
            attrs.extend(("48", "5", "%i" % color))

        if self.bold:
            attrs.append("01")

        if self.underline:
            attrs.append("04")

        if self.italic:
            attrs.append("03")

        return self.escape(attrs)

    def true_color_string(self):
        attrs = []
        if self.fg:
            r,g,b = map(str, to_rgb(self.fg))
            attrs.extend(("38", "2", r, g, b))
        if self.bg:
            r,g,b = map(str, to_rgb(self.bg))
            attrs.extend(("48", "2", r, g, b))
        if self.bold:
            attrs.append("01")
        if self.underline:
            attrs.append("04")
        if self.italic:
            attrs.append("03")
        return self.escape(attrs)

    def reset_string(self):
        """
        tries to minimally reset current terminal state
        ie: only reset fg color and not everything
        """
        attrs = []
        if self.fg is not None:
            attrs.append("39")
        if self.bg is not None:
            attrs.append("49")
        if self.bold or self.underline or self.italic:
            attrs.append("00")
        return self.escape(attrs)

    @staticmethod
    def full_reset_string():
        return EscapeSequence(fg=1, bg=1, bold=1).reset_string()
