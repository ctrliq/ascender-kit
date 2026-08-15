# -*- coding: utf-8 -*-
import code
import sys
from unittest import mock

import pytest

from ascenderkit.scripts import basic_session


@pytest.mark.parametrize('flag', ['-x', '--non-interactive'])
def test_non_interactive_runs_the_session_without_a_prompt(flag):
    """-x was accepted and advertised, but nothing ever read it.

    The session always ended at an interactive prompt, so `ascender-shell -x
    -f script.py` sat waiting for input instead of finishing.
    """
    with mock.patch.object(basic_session, 'main') as main, mock.patch.object(code, 'interact') as interact:
        with mock.patch.object(sys, 'argv', ['ascender-shell', flag]):
            basic_session.load_interactive()

    main.assert_called_once_with()
    interact.assert_not_called()


def test_default_still_opens_a_prompt():
    with mock.patch.object(basic_session, 'main') as main, mock.patch.object(code, 'interact') as interact:
        # No IPython, so the fallback console is what gets used.
        with mock.patch.dict(sys.modules, {'IPython': None}), mock.patch.object(sys, 'argv', ['ascender-shell']):
            basic_session.load_interactive()

    main.assert_called_once_with()
    interact.assert_called_once()


@pytest.mark.parametrize('flag', ['-h', '--help'])
def test_help_neither_connects_nor_prompts(flag):
    with mock.patch.object(basic_session, 'main') as main, mock.patch.object(code, 'interact') as interact:
        with mock.patch.object(sys, 'argv', ['ascender-shell', flag]):
            with pytest.raises(SystemExit):
                basic_session.load_interactive()

    main.assert_not_called()
    interact.assert_not_called()
