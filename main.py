#!/usr/bin/env python

import sys
import consolemd

import logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    with open( sys.argv[1], 'r' ) as f:
        md = f.read()

    renderer = consolemd.Renderer()
    renderer.render( sys.stdout, md )
