# -*- coding: utf-8 -*-
"""Whether a collection the platform serves comes back as a list page.

The registry falls back to a plain ``Base`` for any URL nobody registered, so a
collection the client does not know still answers, but it answers as a scalar.
``count`` reads fine, ``len()`` raises, and each entry in ``results`` is a bare
``PseudoNamespace`` rather than a page, so nothing you just listed can be
fetched, deleted or navigated from.

Thirty two endpoints were in that state when this was written, among them every
user token route, ``receptor_addresses/`` and ``workflow_approval_votes/``.
"""

import re

import pytest

#: Paths whose id segment is not an integer, so the substitution below cannot
#: build one. They are reached from their collection instead.
NON_NUMERIC_ID = re.compile(r'service-index/')


def openapi_paths(connection):
    """Every path under /api/v2/ the platform publishes, with {} for each id."""
    response = connection.get('/api/schema/', headers={'Accept': 'application/json'})
    if response.status_code != 200:
        pytest.skip('this platform publishes no OpenAPI schema at /api/schema/')
    prefix = '/api/v2/'
    return sorted({re.sub(r'\{[^}]+\}', '{}', p[len(prefix) :]) for p in response.json()['paths'] if p.startswith(prefix)})


class Resolver:
    """Turns a path template into one naming objects that exist."""

    def __init__(self, connection):
        self.connection = connection
        self.ids = {}

    def an_id_in(self, collection):
        if collection not in self.ids:
            response = self.connection.get('/api/v2/' + collection, query_parameters={'page_size': 1, 'order_by': 'id'})
            results = response.json().get('results') if response.status_code == 200 else None
            # Not every collection keys its entries on an integer id: the
            # service index uses an ansible id, and settings use a slug.
            an_id = results[0].get('id') if results else None
            self.ids[collection] = str(an_id) if an_id is not None else None
        return self.ids[collection]

    def __call__(self, template):
        resolved, rest = '', template
        while '{}' in rest:
            head, rest = rest.split('{}', 1)
            resolved += head
            an_id = self.an_id_in(resolved)
            if an_id is None:
                return None
            resolved += an_id
        return resolved + rest


def test_every_collection_the_platform_serves_is_a_list_page(api):
    """
    Walk the published paths, and fail on any collection typed as a scalar.

    A path is a collection when the server answers it with ``count`` and
    ``results``. A path whose parent has no objects here cannot be asked, so it
    is skipped rather than guessed at: the sweep is a floor, not a census.
    """
    from ascenderkit.api.pages.page import PageList, get_registered_page

    connection = api.connection
    resolve = Resolver(connection)
    scalars, skipped = [], 0
    for template in openapi_paths(connection):
        if NON_NUMERIC_ID.search(template) and '{}' in template:
            continue
        path = resolve(template)
        if path is None:
            skipped += 1
            continue
        response = connection.get('/api/v2/' + path, headers={'Accept': 'application/json'})
        if 'json' not in response.headers.get('Content-Type', '').lower():
            continue
        body = response.json()
        if not (isinstance(body, dict) and 'count' in body and 'results' in body):
            continue
        if not issubclass(get_registered_page('/api/v2/' + path), PageList):
            scalars.append('%s (asked as %s)' % (template, path))

    assert scalars == [], 'collections the client hands back as a scalar page:\n  ' + '\n  '.join(scalars)
