# -*- coding: utf-8 -*-
"""Whether the endpoints this client declares are ones the server still serves.

``Resources`` is a hand written list of API paths, and nothing checked it. An
entry the platform dropped is not a broken test, it is a 404 handed to whoever
calls that page, from a client that claims to know the API.

Twenty six were dead when this was written: facts, plays and tasks, the old
``permissions`` endpoints, nested schedule routes that never existed, and the
per user settings categories the platform no longer registers.
"""

import re

from ascenderkit.api.resources import Resources

#: Patterns with a wildcard stand for many concrete routes, so a single request
#: says nothing about them. They are checked by the pages that use them.
WILDCARD = re.compile(r'\\w|\[\^|\(\?|\.\*')

#: The id put into a detail path. Its object almost certainly does not exist,
#: which is the point: the reply says whether the route does.
SOME_ID = '1'


def declared():
    """Every concrete endpoint ``Resources`` names, keyed by attribute name."""
    return {
        name.lstrip('_'): value
        for name, value in vars(Resources).items()
        if name.startswith('_') and not name.startswith('__') and isinstance(value, str) and not WILDCARD.search(value)
    }


def test_there_are_endpoints_to_check():
    # The sweep below would pass against an empty list, and this is a hand
    # maintained file, so it is worth saying out loud that it is not empty.
    assert len(declared()) > 200


def test_every_declared_endpoint_is_served(api):
    """
    Ask the server for each path and fail on the ones it does not serve.

    Two different 404s arrive here. Django answers an unrouted path with its own
    HTML page, and the API answers a routed path whose object is missing with
    JSON. So an HTML 404 means the endpoint is gone, whatever the path, and a
    JSON 404 means it is gone only where the path names no id: a collection or a
    fixed path has nothing to be missing.
    """
    connection = api.connection
    gone = []
    for name, pattern in sorted(declared().items()):
        path = pattern.replace(r'\d+', SOME_ID)
        response = connection.get('/api/v2/' + path, headers={'Accept': 'application/json'})
        if response.status_code != 404:
            continue
        unrouted = 'json' not in response.headers.get('Content-Type', '').lower()
        if unrouted or r'\d+' not in pattern:
            gone.append('%s (%s) %s' % (name, pattern, 'is not routed' if unrouted else 'has no such endpoint'))

    assert gone == [], 'declared by this client, not served by the platform:\n  ' + '\n  '.join(gone)
