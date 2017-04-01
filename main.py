#!/usr/bin/env python

import os, sys
import consolemd
import pprint

# idea: decorator that checks if last outputed char (or line?) is a newline
# and sets a variable. really need two newlines though...

class Style(object):
    def __init__(self):
        pass

    def __getattr__(self, name):
        def _ignore(obj, entering):
            return ''
        return _ignore

    def emph(self, obj, entering):
        if entering:
            return '<i>'
        else:
            return '</i>'

    def strong(self, obj, entering):
        if entering:
            return '<b>'
        else:
            return '</b>'

if __name__ == "__main__":
    with open( sys.argv[1], 'r' ) as f:
        md = f.read()

    consolemd = consolemd.ConsoleMD( None, None, Style() )
    consolemd.render( sys.stdout, md )
