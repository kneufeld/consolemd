from __future__ import print_function
import sys
import logging

import colorama
from .terminal256 import EscapeSequence

class ColoredStream( logging.StreamHandler ):

    """
    colorama constants
    use: colorama.Fore.RED + "some string"
    Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Style: DIM, NORMAL, BRIGHT, RESET_ALL
    """

    colors = {
        'DEBUG': EscapeSequence(fg='#ansiblue'),
        'INFO': EscapeSequence(),
        'WARNING': EscapeSequence(fg='#ansiyellow'),
        'ERROR': EscapeSequence(fg='#ansired'),
        'CRITICAL': EscapeSequence(fg='#ansired', bold=True),
    }

    def __init__(self, stream=None):

        # don't output color to pipes or files
        self._enabled = sys.stdout.isatty() and sys.stderr.isatty()

        return super(ColoredStream,self).__init__(stream)

    def emit(self, record):

        try:
            eseq = ColoredStream.colors[record.levelname]
        except KeyError:
            eseq = EscapeSequence()

        msg = self.format(record)

        if self._enabled:
            print( eseq.color_string() + msg + eseq.reset_string(), file=self.stream )
        else:
            self.stream.write( "%s\n" % (msg) )
            self.flush()


def create_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel( logging.NOTSET )

    h1 = ColoredStream( sys.stderr )
    h1.setLevel( logging.INFO )
    h1.set_name( 'stderr' )

    logger.addHandler(h1)

    return logger
