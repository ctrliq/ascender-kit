# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from ascenderkit.api.pages.bulk import Bulk
from ascenderkit.api.pages.host_metrics import HostMetric, HostMetrics
from ascenderkit.api.pages.metrics import Metrics
from ascenderkit.api.pages.page import Page

JSON_HEADERS = {'Accept': 'application/json'}


def make_page(cls, endpoint):
    """Build a page whose connection records the GET it was asked to make."""
    connection = mock.Mock()
    response = mock.Mock()
    response.json.return_value = {'count': 0, 'results': []}
    connection.get.return_value = response
    page = cls(connection, endpoint=endpoint)
    page.page_identity = mock.Mock(return_value=page)
    return page, connection


@pytest.mark.parametrize(
    'cls, endpoint',
    [
        (HostMetric, '/api/v2/host_metrics/'),
        (HostMetrics, '/api/v2/host_metrics/'),
        (Metrics, '/api/v2/metrics/'),
        (Bulk, '/api/v2/bulk/'),
    ],
)
def test_all_pages_is_not_sent_to_the_server(cls, endpoint):
    """all_pages is a client-side flag; forwarding it earns a 400.

    These classes used to override get() with a bare **query_parameters, so
    the caller's all_pages landed in the query string and the server replied
    "HostMetric has no field named 'all_pages'".
    """
    page, connection = make_page(cls, endpoint)
    page.get(all_pages=False)

    query_parameters = connection.get.call_args[0][1]
    assert 'all_pages' not in query_parameters


@pytest.mark.parametrize('cls', [HostMetric, HostMetrics, Metrics, Bulk])
def test_json_is_still_negotiated(cls):
    # These endpoints answer with CSV unless JSON is asked for by name.
    assert cls.get_headers == JSON_HEADERS


def test_ordinary_pages_send_no_special_headers():
    assert Page.get_headers is None


def test_real_query_parameters_are_still_forwarded():
    page, connection = make_page(HostMetrics, '/api/v2/host_metrics/')
    page.get(all_pages=False, hostname='example')

    query_parameters = connection.get.call_args[0][1]
    assert query_parameters == {'hostname': 'example'}
    assert connection.get.call_args[1]['headers'] == JSON_HEADERS
