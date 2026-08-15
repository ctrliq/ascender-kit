# -*- coding: utf-8 -*-
"""Token issuance and the token authentication path.

Upstream removed token auth; Ascender keeps it, so it needs covering here.
"""

import json
import os
import subprocess

import pytest


@pytest.fixture
def token(ascender):
    rc, out, err = ascender('login')
    assert rc == 0, err
    return json.loads(out)['token']


def test_login_issues_a_token(token):
    assert token and len(token) > 20


def test_login_human_format_is_shell_ready(ascender):
    rc, out, err = ascender('login', '-f', 'human')

    assert rc == 0, err
    assert out.strip().startswith('export CONTROLLER_OAUTH_TOKEN=')


def test_a_token_authenticates(ascender, token, insecure):
    """No username or password, only the token."""
    env = {k: v for k, v in os.environ.items() if k not in ('CONTROLLER_USERNAME', 'CONTROLLER_PASSWORD')}
    env['CONTROLLER_OAUTH_TOKEN'] = token

    proc = subprocess.run(['ascender', *insecure, 'me', '-f', 'human'], capture_output=True, text=True, env=env, timeout=300)

    assert proc.returncode == 0, proc.stderr
    assert 'username' in proc.stdout


def test_a_bad_token_is_refused(ascender, insecure):
    env = {k: v for k, v in os.environ.items() if k not in ('CONTROLLER_USERNAME', 'CONTROLLER_PASSWORD')}
    env['CONTROLLER_OAUTH_TOKEN'] = 'not-a-real-token'

    proc = subprocess.run(['ascender', *insecure, 'me'], capture_output=True, text=True, env=env, timeout=300)

    assert proc.returncode != 0


def test_tls_is_verified_without_the_insecure_flag(insecure):
    """Only meaningful where the server's certificate would fail validation."""
    if not insecure:
        pytest.skip('server certificate is trusted, nothing to prove')

    # Drop the environment's opt-out as well as the flag; either one alone
    # still turns verification off, which is what this is checking for.
    env = {k: v for k, v in os.environ.items() if k not in ('CONTROLLER_VERIFY_SSL', 'TOWER_VERIFY_SSL')}

    proc = subprocess.run(['ascender', 'me'], capture_output=True, text=True, env=env, timeout=300)

    assert proc.returncode != 0, 'an untrusted certificate was accepted'
