from io import StringIO
import pytest

# requires pytest-console-scripts

def test_unknown_file(script_runner):
    ret = script_runner.run('consolemd', 'no_such_file')
    assert not ret.success
    assert ret.returncode == 2


def test_readme_file(script_runner):
    ret = script_runner.run('consolemd', 'README.md')
    assert ret.success
    assert "ConsoleMD renders markdown to the console." in ret.stdout


def test_version(script_runner):
    from consolemd import __version__
    ret = script_runner.run('consolemd', '--version')
    assert ret.success
    assert ret.stdout.strip() == __version__
    assert ret.stderr == ''


def test_readme_file_with_all_args(script_runner):
    ret = script_runner.run('consolemd', '-d', '--color', '--true-color', '--soft-wrap', '-w', '10', '-s', 'native', 'README.md')
    assert ret.success
    assert ret.stdout != ''
    assert ret.stderr != ''


def test_pipe_empty_stdin(script_runner):
    stdin = StringIO()
    ret = script_runner.run('consolemd', stdin=stdin)
    assert ret.success
    assert ret.stdout == ''
    assert ret.stderr == ''


def test_pipe_stdin(script_runner):
    input = "ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ"
    stdin = StringIO(input)
    ret = script_runner.run('consolemd', stdin=stdin)
    assert ret.success
    assert ret.stdout == input + '\n'
    assert ret.stderr == ''
