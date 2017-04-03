# ConsoleMD

ConsoleMD renders markdown to the console.

## Installation

It's highly recommended to install ConsoleMD inside a virtual environment.

```bash
pip install consolemd
```

## Why not just use pygments?

Because pygments highlights the markdown but doesn't strip out
the control characters. Also, ConsoleMD uses CommonMark to parse
the markdown instead of the lousy one in pygments _(I'm allowed to
say that since I'm the guy that wrote it)_.

Also, ConsoleMD uses some parts of pygments internally, and uses
pygments to highlight code blocks.

## CommonMark

Over the last few years there's been work on standardizing markdown
with an official spec, that work happens at [CommonMark.org](http://commonmark.org/).

The python implementation of the specification that I used is
called [CommonMark-py](https://github.com/rtfd/CommonMark-py).

Github has recently (March 2017) converted all internal markdown
to use a CommonMark parser, an interesting article can be found
[here](https://githubengineering.com/a-formal-spec-for-github-markdown/).
