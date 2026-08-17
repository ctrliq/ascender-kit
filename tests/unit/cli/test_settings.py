# -*- coding: utf-8 -*-
import argparse
from unittest import mock

import pytest

from ascenderkit.cli.custom import SettingsModify


def build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    subparsers.add_parser('modify')
    return subparsers


def settings_page(actions):
    """A settings page whose OPTIONS carries `actions`."""
    options = mock.Mock()
    options.json = {'actions': actions}
    page = mock.Mock()
    page.endpoint = '/api/v2/settings/'
    page.__class__ = mock.Mock(return_value=mock.Mock(options=mock.Mock(return_value=options)))
    return page


@pytest.mark.parametrize(
    'actions, expected',
    [
        ({'GET': {}, 'PUT': {'AWX_A': {}, 'AWX_B': {}}}, ['AWX_A', 'AWX_B']),
        # A user who may not change settings is served no PUT section. Reading
        # straight through it raised KeyError('PUT'), which took down the whole
        # resource -- `settings list` could not run either.
        ({'GET': {}}, []),
        ({}, []),
    ],
)
def test_settable_keys_track_what_the_server_allows(actions, expected):
    subparsers = build_parser()
    SettingsModify(settings_page(actions)).add_arguments(subparsers, mock.Mock())

    key_action = next(a for a in subparsers.choices['modify']._actions if a.dest == 'key')
    assert sorted(key_action.choices) == expected


def test_no_put_section_does_not_raise():
    subparsers = build_parser()
    SettingsModify(settings_page({'GET': {}})).add_arguments(subparsers, mock.Mock())
