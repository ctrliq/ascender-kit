# -*- coding: utf-8 -*-
import logging
from unittest import mock

from ascenderkit.api.pages.api import ApiV2, EXPORTABLE_RESOURCES


def build_api(matched):
    """An ApiV2 whose filtered lookups return `matched` results."""
    api = ApiV2.__new__(ApiV2)
    for resource in EXPORTABLE_RESOURCES:
        api.__dict__[resource] = mock.Mock()
    listing = mock.Mock()
    listing.results = matched
    api._filtered_list = mock.Mock(return_value=listing)
    api._export_list = mock.Mock(return_value=list(matched))
    return api


def test_selector_matching_nothing_is_reported(caplog):
    # An empty export looks exactly like a successful one, so a mistyped name
    # would otherwise be silent.
    api = build_api([])
    with caplog.at_level(logging.WARNING):
        data = api.export_assets(users=['no-such-user'])

    assert data['users'] == []
    assert "No users matched ['no-such-user']" in caplog.text


def test_selector_that_matches_is_silent(caplog):
    api = build_api([mock.Mock()])
    with caplog.at_level(logging.WARNING):
        api.export_assets(users=['admin'])

    assert 'matched' not in caplog.text


def test_exporting_everything_does_not_warn(caplog):
    # No selectors at all means "export everything", where an empty resource is
    # ordinary rather than suspicious.
    api = build_api([])
    api._export_list = mock.Mock(return_value=[])
    with caplog.at_level(logging.WARNING):
        api.export_assets()

    assert 'matched' not in caplog.text
    api._filtered_list.assert_not_called()
