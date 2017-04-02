from setuptools import setup, find_packages

setup(
    name='consolemd',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Click',
        'pygments',
        'setproctitle',
        'commonmark',
    ],
    entry_points='''
        [console_scripts]
        consolemd=consolemd.cli:cli
    ''',
)
