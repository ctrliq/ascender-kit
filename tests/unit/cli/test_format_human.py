# -*- coding: utf-8 -*-
import re

import pytest

from ascenderkit.cli.format import format_human


def digits(text):
    """Strip whatever thousands separator the ambient locale uses."""
    return re.sub(r'[^0-9-]', '', text)


def render(results, fmt='id,name'):
    return format_human({'count': len(results), 'results': results}, fmt)


@pytest.mark.parametrize('value, expected', [(0, '0'), (7, '7'), (1234, '1234'), (1234567, '1234567'), (-42, '-42')])
def test_numeric_columns_render(value, expected):
    """Numbers go through locale.format_string, which is version-sensitive.

    locale.format() was removed in Python 3.12, so this line raised
    AttributeError on three of the four interpreters this package claims to
    support, and `-f human` fell over on any numeric field.
    """
    out = render([{'id': value, 'name': 'thing'}])

    assert digits(out.splitlines()[2].split()[0]) == expected


def test_large_numbers_do_not_raise_under_grouping():
    # grouping=True is passed, so the separator depends on the locale; the
    # digits must survive whatever it does.
    out = render([{'id': 9876543, 'name': 'x'}])

    assert digits(out).startswith('9876543')


@pytest.mark.parametrize(
    'value, expected',
    [
        (None, ''),
        ('text', 'text'),
        ([1, 2], '[1, 2]'),
        ({'a': 1}, '{"a": 1}'),
    ],
)
def test_non_numeric_values_fall_back(value, expected):
    out = render([{'id': 1, 'name': value}])

    assert expected in out


def test_table_shape():
    out = render([{'id': 1, 'name': 'alpha'}, {'id': 22, 'name': 'beta'}])
    lines = out.splitlines()

    assert lines[0].split() == ['id', 'name']
    assert set(lines[1].strip()) == {'=', ' '} - {' '} or '=' in lines[1]
    assert len(lines) == 4  # header, rule, two rows


def test_a_single_object_renders_without_a_count():
    out = format_human({'id': 3, 'name': 'solo'}, 'id,name')

    assert 'solo' in out
    assert digits(out.splitlines()[2].split()[0]) == '3'
