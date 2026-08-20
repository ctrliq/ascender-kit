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


class ItemClass:
    """Stands in for a page's ``__item_class__``, which the export reads by name."""


class RelatedEndpoint:
    """A related endpoint, e.g. /api/v2/projects/1/webhook_key/.

    ``NATURAL_KEY`` is None on the base page class, which is what an endpoint
    that carries no natural key of its own resolves to.
    """

    __item_class__ = ItemClass

    def __init__(self, natural_key=None):
        self.NATURAL_KEY = natural_key

    def _create(self):
        return self

    def get_natural_key(self, cache=None):
        return {'type': 'organization', 'name': 'Default'} if self.NATURAL_KEY else None


class ExportedPage:
    """The object being exported, carrying one related field."""

    __item_class__ = ItemClass
    endpoint = '/api/v2/projects/1/'

    def __init__(self, key, related_endpoint):
        self.json = {'name': 'Example', key: 'the-value'}
        self.related = {key: related_endpoint}

    def get_natural_key(self, cache=None):
        return {'type': 'project', 'name': 'Example'}


def build_export_api(related_endpoint):
    """An ApiV2 whose page cache resolves every related link to one endpoint."""
    api = ApiV2.__new__(ApiV2)
    api._has_error = False
    api._cache = mock.Mock()
    api._cache.get_page.return_value = related_endpoint
    return api


def test_related_without_a_natural_key_is_skipped_quietly(caplog):
    # webhook_key is write-only and its endpoint has no natural key, so there is
    # no portable way to reference it and skipping it is the expected outcome.
    # Reporting that as a warning printed on a successful export, and the
    # ctrliq.ascender collection gobbles these loggers looking for failures.
    related_endpoint = RelatedEndpoint()
    api = build_export_api(related_endpoint)

    with caplog.at_level(logging.DEBUG):
        fields = api._export(ExportedPage('webhook_key', related_endpoint), {'name': {'type': 'string'}, 'webhook_key': {'type': 'string'}})

    assert 'webhook_key' not in fields
    assert fields['name'] == 'Example'
    assert api._has_error is False
    assert [record for record in caplog.records if record.levelno >= logging.WARNING] == []
    assert 'the related endpoint has no natural key' in caplog.text


def test_related_with_a_natural_key_is_exported(caplog):
    # The counterpart: a related field that can be referenced still is, so the
    # skip above is not swallowing ordinary foreign keys.
    related_endpoint = RelatedEndpoint(natural_key=('name',))
    api = build_export_api(related_endpoint)

    with caplog.at_level(logging.DEBUG):
        fields = api._export(ExportedPage('organization', related_endpoint), {'name': {'type': 'string'}, 'organization': {'type': 'id'}})

    assert fields['organization'] == {'type': 'organization', 'name': 'Default'}
    assert api._has_error is False
    assert 'no natural key' not in caplog.text
