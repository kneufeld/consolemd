from io import StringIO

# requires pytest-console-scripts

def test_unknown_file(script_runner):
    ret = script_runner.run('consolemd', 'no_such_file')
    assert not ret.success
    assert ret.returncode == 2


def test_readme_file(script_runner):
    ret = script_runner.run('consolemd', 'README.md')
    assert ret.success
    assert "ConsoleMD renders markdown to the console." in ret.stdout


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
