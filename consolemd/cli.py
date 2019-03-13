"""
ConsoleMD renders markdown to the console instead of just syntax
highlighting the markdown. The difference being that the control
characters are stripped.
"""

import os
import sys
import click

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

    def get_handler(name):
        handlers = [
            h for h in logger.handlers
            if h.get_name() == name
        ]
        if handlers:
            return handlers[0]

    if param.name == 'debug' and value:
        logger.setLevel(logging.DEBUG)
        handler = get_handler('stderr')
        if handler:
            handler.setLevel(logging.DEBUG)
    elif param.name == 'quiet' and value:
        logger.setLevel(logging.WARNING)
        handler = get_handler('stderr')
        if handler:
            handler.setLevel(logging.WARNING)


def get_width(ctx, param, value):
    min_width = 20
    width = None

    if value:
        width = value
    else:
        # if one of these env var is set, use it
        for key in ['CONSOLEMD_WIDTH', 'MANWIDTH']:
            value = os.environ.get(key, None)
            if value is not None:
                width = int(value)
                logger.debug("using envvar %s to set width to %d", key, width)
                break

    if width is not None and width < min_width:
        logger.warning("overriding width to %d", min_width)
        width = min_width

    if width is not None:
        logger.debug("using width of %d", width)

    return width

# this is a click related function, not logging per se, hence it lives here
def enable_color(ctx, param, value):
    if value is False:
        for h in logger.handlers:
            h._enabled = False


def set_true_color(ctx, param, value):
    import consolemd.escapeseq
    consolemd.escapeseq._true_color = value


def verify_style_name(ctx, param, value):
    import pygments.styles
    import pygments.util

    try:
        pygments.styles.get_style_by_name(value)
        return value
    except pygments.util.ClassNotFound:
        ctx.fail("invalid style name: {}".format(value))

def show_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    from . import __version__
    click.echo(__version__)
    ctx.exit()

CTX_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CTX_SETTINGS)
@click.option('--version',
        is_flag=True, callback=show_version, expose_value=False, is_eager=True,
        help="show version and exit")
@click.option('-d', '--debug',
        is_flag=True, callback=change_loglevel, expose_value=True, is_eager=True,
        help="show extra info")
@click.option('-q', '--quiet',
        is_flag=True, callback=change_loglevel, expose_value=True, is_eager=True,
        help="show less info")
@click.option('--color/--no-color',
        default=True, callback=enable_color, is_eager=True,
        help="enable/disable logging color")
@click.option('--true-color/--no-true-color',
        default=os.environ.get('CONSOLEMD_TRUECOL', True),
        callback=set_true_color, is_eager=True,
        help="enable/disable true color (16m colors)")
@click.option('--soft-wrap/--no-soft-wrap',
        default=os.environ.get('CONSOLEMD_WRAP', True),
        help="output lines wrap along with source lines")
@click.option('-w', '--width',
        callback=get_width, expose_value=True, is_eager=False, type=int,
        help="format text to given width, othewise use soft-wrap")
@click.option('-o', '--output',
        type=click.File('w'), default=sys.stdout,
        help="output to a file, stdout by default")
@click.option('-s', '--style',
        type=str, default=os.environ.get('CONSOLEMD_STYLE', 'native'),
        callback=verify_style_name, is_eager=True,
        help="what pygments style to use for coloring (def: native)")
@click.argument('input', type=click.File('r'), default=sys.stdin)
@click.pass_context
def cli(ctx, input, **kw):
    """
    render some markdown
    """

    rename_proc( 'consolemd' )

    md = input.read()

    import consolemd
    renderer = consolemd.Renderer(style_name=kw['style'])
    renderer.render( md, **kw )

if __name__ == "__main__":
    cli()
