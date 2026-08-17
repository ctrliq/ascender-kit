# -*- coding: utf-8 -*-
import pytest

from ascenderkit.api import utils

ENCRYPTED = '$encrypted$'


@pytest.mark.parametrize(
    'value, expected',
    [
        (ENCRYPTED, ''),
        ('plain', 'plain'),
        ({'password': ENCRYPTED, 'username': 'alice'}, {'password': '', 'username': 'alice'}),
        ([ENCRYPTED, 'plain'], ['', 'plain']),
    ],
)
def test_remove_encrypted_blanks_placeholders(value, expected):
    assert utils.remove_encrypted(value) == expected


@pytest.mark.parametrize(
    'value, expected',
    [
        ('plain', 'plain'),
        (7, 7),
        (None, None),
        # The key goes away rather than being blanked, so the server applies
        # its own default instead of storing an empty secret.
        ({'password': ENCRYPTED, 'username': 'alice'}, {'username': 'alice'}),
        ({'inputs': {'password': ENCRYPTED, 'username': 'alice'}}, {'inputs': {'username': 'alice'}}),
        ([ENCRYPTED, 'plain'], ['plain']),
        ({'a': {'b': [ENCRYPTED, 'keep']}}, {'a': {'b': ['keep']}}),
        ({'nothing': 'to strip'}, {'nothing': 'to strip'}),
    ],
)
def test_drop_encrypted_removes_placeholders(value, expected):
    assert utils.drop_encrypted(value) == expected


def test_drop_encrypted_leaves_the_original_untouched():
    payload = {'password': ENCRYPTED, 'username': 'alice'}
    utils.drop_encrypted(payload)
    assert payload == {'password': ENCRYPTED, 'username': 'alice'}


def test_drop_encrypted_keeps_values_that_merely_contain_the_token():
    # Only an exact match is a placeholder; a real secret that happens to
    # start with the token is still a value the caller meant to send.
    payload = {'password': '$encrypted$abc123'}
    assert utils.drop_encrypted(payload) == payload
