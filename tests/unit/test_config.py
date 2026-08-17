# -*- coding: utf-8 -*-
import importlib

import pytest


def reload_config(monkeypatch, **env):
    for key in ('ASCENDERKIT_PROJECT_FILE', 'ASCENDERKIT_CREDENTIAL_FILE', 'ASCENDERKIT_BASE_URL'):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # `ascenderkit.config` the name resolves to the config object, because the
    # package __init__ imports it over the submodule, so ask importlib for the
    # module itself rather than going through the attribute.
    module = importlib.import_module('ascenderkit.config')

    return importlib.reload(module).config


def test_project_file_is_actually_read(monkeypatch, tmp_path):
    """The path was taken from `config` rather than the environment.

    The guard checked os.getenv, so the block ran, but the value handed to
    load_projects was None -- which it treats as "no file given" and answers
    with {}. The file named by the variable was never opened.
    """
    projects = tmp_path / 'projects.yml'
    projects.write_text('git:\n  default: https://example.org/repo.git\n')

    config = reload_config(monkeypatch, ASCENDERKIT_PROJECT_FILE=str(projects))

    assert config.project_urls == {'git': {'default': 'https://example.org/repo.git'}}


def test_a_project_file_that_is_not_there_is_reported(monkeypatch, tmp_path):
    missing = tmp_path / 'absent.yml'

    with pytest.raises(Exception, match='Unable to load projects file'):
        reload_config(monkeypatch, ASCENDERKIT_PROJECT_FILE=str(missing))


def test_credential_file_is_read(monkeypatch, tmp_path):
    creds = tmp_path / 'credentials.yml'
    creds.write_text('default:\n  username: someone\n  password: secret\n')

    config = reload_config(monkeypatch, ASCENDERKIT_CREDENTIAL_FILE=str(creds))

    assert config.credentials['default']['username'] == 'someone'


def test_no_project_file_leaves_it_unset(monkeypatch):
    config = reload_config(monkeypatch)

    assert config.get('project_urls') is None
