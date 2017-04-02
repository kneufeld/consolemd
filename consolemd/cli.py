# -*- coding: utf-8 -*-

"""
ConsoleMD renders markdown to the console instead of just syntax
highlighting the markdown. The difference being that the control
characters are stripped.
"""

import sys

import click
import consolemd

import logging
from .logger import create_logger
logger = create_logger('consolemd')


def rename_proc( name ):
    """
    rename executabe from 'python <name>' to just '<name>'
    you can't show arguments because then `pidof <name>` would fail
    """
    from setproctitle import setproctitle
    setproctitle( name )


# this is a click related function, not logging per se, hence it lives here
def change_loglevel(ctx, param, value):
    # 'stdout' is the name of a handler defined in .logger

    if param.name == 'debug' and value:
        logger.setLevel( logging.DEBUG )
        filter( lambda h: h.get_name() == 'stderr', logger.handlers )[0].setLevel( logging.DEBUG )
    elif param.name == 'quiet' and value:
        logger.setLevel( logging.WARNING )
        filter( lambda h: h.get_name() == 'stderr', logger.handlers )[0].setLevel( logging.WARNING )


# this is a click related function, not logging per se, hence it lives here
def enable_color(ctx, param, value):
    if value == False:
        for h in logger.handlers:
            h._enabled = False


CTX_SETTINGS=dict(help_option_names=['-h','--help'])

@click.command(context_settings=CTX_SETTINGS)
@click.option('-d','--debug',
        is_flag=True, callback=change_loglevel, expose_value=True, is_eager=True,
        help="show extra info")
@click.option('-q','--quiet',
        is_flag=True, callback=change_loglevel, expose_value=True, is_eager=True,
        help="show less info")
@click.option('--color/--no-color',
        default=True, callback=enable_color, is_eager=True,
        help="enable/disable color output")
@click.option('-o','--output',
        type=click.File('wb'), default=sys.stdout,
        help="output to a file, stdout by default")
@click.argument('input', type=click.File('rb'))
@click.pass_context
def cli(ctx, input, **kw):
    """
    render some markdown
    """

    rename_proc( 'consolemd' )

    md = input.read()

    renderer = consolemd.Renderer()
    renderer.render( kw['output'], md )

if __name__ == "__main__":
    cli()
