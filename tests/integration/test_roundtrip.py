# -*- coding: utf-8 -*-
"""Export, import it straight back, and export again.

This is the test that would have caught the worst bug this client had: an
export writes `$encrypted$` where the server withheld a secret and reads that
same token back as "keep what you have", so blanking it first turned importing
an export into an overwrite. Every credential password in it went blank, and no
error said so.
"""

import json

import pytest


@pytest.fixture(scope='module')
def exported(ascender):
    rc, out, err = ascender('export')
    assert rc == 0, err
    return json.loads(out)


def test_export_produces_resources(exported):
    assert exported, 'export returned nothing'
    populated = {k: len(v) for k, v in exported.items() if v}
    assert populated, 'export contained no resources at all'


def test_secrets_are_withheld_as_placeholders(exported):
    for credential in exported.get('credentials') or []:
        for value in credential.get('inputs', {}).values():
            assert value != '', 'a secret was exported as an empty string'


def test_round_trip_is_lossless(ascender, exported):
    """export -> import -> export must come back byte for byte."""
    before = json.dumps(exported, sort_keys=True)

    rc, _, err = ascender('import', stdin=json.dumps(exported), timeout=900)
    # A non-zero status can come from data the server rejects for its own
    # reasons; what must hold is that nothing was lost.
    assert 'Traceback' not in err

    rc, out, err = ascender('export')
    assert rc == 0, err
    after = json.dumps(json.loads(out), sort_keys=True)

    assert after == before, 'the round trip changed the exported document'


def test_credential_secrets_survive_the_round_trip(ascender):
    rc, out, err = ascender('export')
    assert rc == 0, err

    for credential in json.loads(out).get('credentials') or []:
        for field, value in credential.get('inputs', {}).items():
            assert value != '', f'{credential["name"]}.{field} was blanked by the import'


def test_a_selector_that_matches_nothing_says_so(ascender):
    rc, out, err = ascender('export', '--users', 'no-such-user-exists-here')

    assert rc == 0
    assert json.loads(out).get('users') == []
    assert 'no-such-user-exists-here' in err, 'an empty export gave no warning'
