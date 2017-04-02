#!/usr/bin/env python

import os, sys
import consolemd
import pprint

import logging
logging.basicConfig(level=logging.DEBUG)

# idea: decorator that checks if last outputed char (or line?) is a newline
# and sets a variable. really need two newlines though...

if __name__ == "__main__":
    with open( sys.argv[1], 'r' ) as f:
        md = f.read()

    consolemd = consolemd.ConsoleMD()
    consolemd.render( sys.stdout, md )
