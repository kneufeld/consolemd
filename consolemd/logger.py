# -*- coding: utf-8 -*-

import sys
import logging

from .escapeseq import EscapeSequence

class ColoredStream( logging.StreamHandler ):
    colors = {
        'DEBUG'    : EscapeSequence(fg='#ansiblue'),
        'INFO'     : EscapeSequence(),
        'WARNING'  : EscapeSequence(fg='#ansiyellow'),
        'ERROR'    : EscapeSequence(fg='#ansired', bg='#400000'),
        'CRITICAL' : EscapeSequence(fg='#ansired', bg='#400000', bold=True),
    }

    def __init__(self, stream=None):
        # don't output color to pipes or files
        self._enabled = sys.stderr.isatty()
        return super(ColoredStream,self).__init__(stream)

    def emit(self, record):

        try:
            eseq = ColoredStream.colors[record.levelname]
        except KeyError:
            eseq = EscapeSequence()

        msg = self.format(record)

        if self._enabled:
            self.stream.write( "{}{}{}\n".format(eseq, msg, eseq.reset_string()) )
        else:
            self.stream.write( "{}\n".format(msg) )

        self.flush()


def create_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel( logging.NOTSET )

    h1 = ColoredStream( sys.stderr )
    h1.setLevel( logging.INFO )
    h1.set_name( 'stderr' )

    logger.addHandler(h1)

    return logger
