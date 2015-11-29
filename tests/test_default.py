"""Test against sample modules using the default options."""

import os

import flake8.main
import pytest

EXPECTED = """\
./sample.py:1:1: D100 Missing docstring in public module
./sample.py:5:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample.py:5:1: D401 First line should be in imperative mood ('Print', not 'Prints')
./sample.py:14:1: D203 1 blank line required before class docstring (found 0)
./sample.py:14:1: D204 1 blank line required after class docstring (found 0)
./sample.py:14:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample_unicode.py:1:1: D100 Missing docstring in public module
./sample_unicode.py:15:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample_unicode.py:15:1: D401 First line should be in imperative mood ('Print', not 'Prints')
./sample_unicode.py:24:1: D203 1 blank line required before class docstring (found 0)
./sample_unicode.py:24:1: D204 1 blank line required after class docstring (found 0)
./sample_unicode.py:24:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
"""


@pytest.mark.parametrize('stdin', ['', 'sample_unicode.py', 'sample.py'])
def test_direct(capsys, monkeypatch, tempdir, stdin):
    """Test by calling flake8.main.main() using the same running python process.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param tempdir: conftest fixture.
    :param str stdin: Pipe this file to stdin of flake8.
    """
    # Prepare.
    monkeypatch.chdir(tempdir.join('empty' if stdin else ''))
    monkeypatch.setattr('sys.argv', ['flake8', '-' if stdin else '.', '-j1'])
    if stdin:
        monkeypatch.setattr('pep8.stdin_get_value', lambda: tempdir.join(stdin).read())

    # Execute.
    with pytest.raises(SystemExit):
        flake8.main.main()
    out, err = capsys.readouterr()
    assert not err

    if stdin:
        expected = '\n'.join('stdin:' + l.split(':', 1)[-1] for l in EXPECTED.splitlines() if stdin in l)
    elif os.name == 'nt':
        expected = EXPECTED.replace('./sample', r'.\sample')
    else:
        expected = EXPECTED

    assert expected.strip() == out.strip()
