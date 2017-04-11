# -*- coding: utf-8 -*-

"""
contains color utility functions and xterm color data
"""

# Default mapping of #ansixxx to RGB colors.
ansicolors = {
    # dark
    '#ansiblack'     : '#000000',
    '#ansidarkred'   : '#7f0000',
    '#ansidarkgreen' : '#007f00',
    '#ansibrown'     : '#7f7fe0',
    '#ansidarkblue'  : '#40407f', # lighter than normal
    '#ansipurple'    : '#7f007f',
    '#ansiteal'      : '#007f7f',
    '#ansilightgray' : '#e5e5e5',
    # normal
    '#ansidarkgray'  : '#555555',
    '#ansired'       : '#ff0000',
    '#ansigreen'     : '#00ff00',
    '#ansiyellow'    : '#ffff00',
    '#ansiblue'      : '#6060ff', # lighter than normal
    '#ansifuchsia'   : '#ff00ff',
    '#ansiturquoise' : '#00ffff',
    '#ansiwhite'     : '#ffffff',
}

def _build_color_table():
    # colors 0..15: 16 basic colors

    xterm_colors = []

    xterm_colors.append((0x00, 0x00, 0x00))  # 0
    xterm_colors.append((0xcd, 0x00, 0x00))  # 1
    xterm_colors.append((0x00, 0xcd, 0x00))  # 2
    xterm_colors.append((0xcd, 0xcd, 0x00))  # 3
    xterm_colors.append((0x00, 0x00, 0xee))  # 4
    xterm_colors.append((0xcd, 0x00, 0xcd))  # 5
    xterm_colors.append((0x00, 0xcd, 0xcd))  # 6
    xterm_colors.append((0xe5, 0xe5, 0xe5))  # 7
    xterm_colors.append((0x7f, 0x7f, 0x7f))  # 8
    xterm_colors.append((0xff, 0x00, 0x00))  # 9
    xterm_colors.append((0x00, 0xff, 0x00))  # 10
    xterm_colors.append((0xff, 0xff, 0x00))  # 11
    xterm_colors.append((0x5c, 0x5c, 0xff))  # 12
    xterm_colors.append((0xff, 0x00, 0xff))  # 13
    xterm_colors.append((0x00, 0xff, 0xff))  # 14
    xterm_colors.append((0xff, 0xff, 0xff))  # 15

    # colors 16..232: the 6x6x6 color cube

    valuerange = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)

    for i in range(217):
        r = valuerange[(i // 36) % 6]
        g = valuerange[(i // 6) % 6]
        b = valuerange[i % 6]
        xterm_colors.append((r, g, b))

    # colors 233..253: grayscale

    for i in range(1, 22):
        v = 8 + i * 10
        xterm_colors.append((v, v, v))

    return xterm_colors

def to_rgb(color):
    """
    return r,g,b integers from #colorstring
    """
    color = ansicolors.get(color, color)

    if color[0] == '#':
        color = color[1:]

    color = int(color, 16)

    r = (color >> 16) & 0xff
    g = (color >> 8) & 0xff
    b = color & 0xff

    return r,g,b


def from_rgb(r,g,b):
    """
    return #colorstring from r,g,b integers
    """
    # hex() produces "0x08", we want just "08"
    rgb = [hex(i)[2:].zfill(2) for i in map(int, [r,g,b])]
    return "#" + "".join(rgb)


def reshade( color, per):
    """
    given a #colorstring and a percentage, darken/lighten each
    r,g,b channel
    """
    def scale(c, per):
        return max(0, min(255, int(c*per)))

    if not color:
        return ''

    if per == 1.0:
        return color

    r,g,b = to_rgb(color)
    r,g,b = map( lambda c: scale(c,per), [r,g,b] )
    return from_rgb(r,g,b)


class ColorMap(object):
    """
    return the closest xterm color index based on a #colorstring
    """

    # only called once for all ColorMap instances
    xterm_colors = _build_color_table()

    def __init__(self, color):
        """
        color can be a name (eg. #ansiyellow) or value (eg. #fe348c)
        """
        self._color = ansicolors.get(color, color)

    @property
    def color(self):
        """
        by returning an index, we're using a built-in xterm color in the console
        """
        return self._color_index(self._color)

    def _closest_color(self, r, g, b):
        distance = 257*257*3  # "infinity" (>distance from #000000 to #ffffff)
        match = 0

        for i in range(0, 254):
            values = self.xterm_colors[i]

            rd = r - values[0]
            gd = g - values[1]
            bd = b - values[2]
            d = rd*rd + gd*gd + bd*bd

            if d < distance:
                match = i
                distance = d

        return match

    def _color_index(self, color):
        if color in ansicolors:
            color = ansicolors[color]

        color = color[1:]

        try:
            rgb = int(str(color), 16)
        except ValueError:
            rgb = 0

        r = (rgb >> 16) & 0xff
        g = (rgb >> 8) & 0xff
        b = rgb & 0xff

        return self._closest_color(r, g, b)
