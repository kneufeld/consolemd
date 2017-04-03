# -*- coding: utf-8 -*-

"""
ConsoleMD parses markdown using CommonMark-py (implementation of the
CommonMarkdown spec) and then fully renders it to the console in true color.
"""

import os
from setuptools import setup

base_dir = os.path.dirname(os.path.abspath(__file__))
pkg_name = 'consolemd'

# adapted from: http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def pseudo_import( pkg_name ):
    """
    return a new module that contains the variables of pkg_name.__init__
    """
    init = os.path.join( pkg_name, '__init__.py' )

    # remove imports and 'from foo import'
    lines = open(init,'r').readlines()
    lines = filter( lambda l: not l.startswith('from'), lines)
    lines = filter( lambda l: not l.startswith('import'), lines)

    code = '\n'.join(lines)

    import imp
    module = imp.new_module(pkg_name)

    exec code in module.__dict__
    return module

# trying to make this setup.py as generic as possible
module = pseudo_import(pkg_name)

setup(
    name=pkg_name,
    packages=[pkg_name],

    install_requires=[
        'click<7.0',
        'pygments<3.0',
        'setproctitle<1.2',
        'commonmark<1.0',
    ],

    entry_points='''
        [console_scripts]
        consolemd=consolemd.cli:cli
    ''',

    # metadata for upload to PyPI
    description      = "ConsoleMD renders markdown to the console",
    long_description = __doc__,
    version          = module.__version__,
    author           = module.__author__,
    author_email     = module.__author_email__,
    license          = module.__license__,
    keywords         = "markdown console terminal".split(),
    url              = module.__url__,

    classifiers      = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        ],

    data_files       = [],
)
