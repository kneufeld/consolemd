#!/usr/bin/env python

import os, sys
import consolemd
import pprint

import logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    with open( sys.argv[1], 'r' ) as f:
        md = f.read()

    renderer = consolemd.Renderer()
    renderer.render( sys.stdout, md )
