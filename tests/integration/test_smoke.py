# -*- coding: utf-8 -*-
"""Every resource the server advertises should list in every output format."""

import json

import pytest


def discovered_resources(ascender):
    rc, out, _ = ascender('--help')
    assert rc == 0
    body = out.split('positional arguments')[-1].split('options:')[0]
    return [line.split()[0] for line in body.splitlines() if line.startswith('    ') and line.strip() and not line.startswith('     ')]


def test_help_lists_resources(ascender):
    """`ascender --help` is the only way to discover the command set."""
    rc, out, _ = ascender('--help')

    assert rc == 0
    for expected in ('config', 'export', 'import', 'me', 'organizations'):
        assert expected in out


def test_every_resource_lists(ascender):
    """Each resource, once. Every CLI run pays a login, so formats are covered
    separately rather than multiplying this by three."""
    resources = discovered_resources(ascender)
    assert len(resources) > 20, 'suspiciously few resources discovered'

    failures = []
    for resource in resources:
        if resource in ('login', 'import', 'export', 'config'):
            continue
        rc, _, err = ascender(resource, 'list')
        if rc != 0 and "invalid choice: 'list'" not in err:
            failures.append((resource, rc, err.strip().splitlines()[-1:]))

    assert not failures, f'resources failed to list: {failures}'


@pytest.mark.parametrize('fmt', ['json', 'yaml', 'human', 'jq'])
def test_each_output_format(ascender, fmt):
    """Formatters are not resource-specific, so one resource proves them."""
    args = ['organizations', 'list', '-f', fmt] + (['--filter', '.count'] if fmt == 'jq' else [])
    rc, out, err = ascender(*args)

    if fmt == 'jq' and 'jq dependency' in err:
        pytest.skip('the optional jq extra is not installed')
    assert rc == 0, err
    assert out.strip()


def test_control_resources(ascender):
    for resource in ('ping', 'me', 'config', 'metrics'):
        rc, out, err = ascender(resource)
        assert rc == 0, f'{resource} failed: {err}'
        assert out.strip()


def test_paging_returns_every_record(api):
    """all_pages must walk every page and repeat none of them.

    A deliberately tiny page size proves the loop over several pages without
    dragging thousands of records across the wire; the volume never added
    anything the assertions could see.
    """
    paged = api.organizations.get(all_pages=True, page_size=1)
    if paged.count < 3:
        pytest.skip('need at least three organizations to span several pages')

    ids = [record['id'] for record in paged.results]
    # Compare only against the count reported by the same response. Another
    # test may be writing to this server, so a count read separately could
    # legitimately disagree by the time the walk finishes.
    assert len(ids) == paged.count, 'paging dropped records'
    assert len(set(ids)) == len(ids), 'paging returned duplicate records'
