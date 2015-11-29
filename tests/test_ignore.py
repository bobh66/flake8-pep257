"""Test against sample modules using the ignore option in all supported config sources."""

import os

import flake8.main
import pytest

EXPECTED = """\
./sample.py:1:1: D100 Missing docstring in public module
./sample.py:5:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample.py:5:1: D401 First line should be in imperative mood ('Print', not 'Prints')
./sample.py:14:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample_unicode.py:1:1: D100 Missing docstring in public module
./sample_unicode.py:15:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
./sample_unicode.py:15:1: D401 First line should be in imperative mood ('Print', not 'Prints')
./sample_unicode.py:24:1: D300 Use \"\"\"triple double quotes\"\"\" (found '''-quotes)
"""


@pytest.mark.parametrize('ignore', ['D203,D204', 'D2'])
@pytest.mark.parametrize('stdin', ['', 'sample_unicode.py', 'sample.py'])
@pytest.mark.parametrize('which_cfg', ['tox.ini', 'tox.ini flake8', 'setup.cfg', '.pep257'])
def test_direct(capsys, monkeypatch, tempdir, ignore, stdin, which_cfg):
    """Test by calling flake8.main.main() using the same running python process.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param tempdir: conftest fixture.
    :param str ignore: Config value for ignore option.
    :param str stdin: Pipe this file to stdin of flake8.
    :param str which_cfg: Which config file to test with.
    """
    # Prepare.
    monkeypatch.chdir(tempdir.join('empty' if stdin else ''))
    monkeypatch.setattr('sys.argv', ['flake8', '-' if stdin else '.', '-j1'])
    if stdin:
        monkeypatch.setattr('pep8.stdin_get_value', lambda: tempdir.join(stdin).read())

    # Write configuration.
    cfg = which_cfg.split()
    section = cfg[1] if len(cfg) > 1 else 'pep257'
    tempdir.join('empty' if stdin else '', cfg[0]).write('[{0}]\nignore = {1}\n'.format(section, ignore))

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
