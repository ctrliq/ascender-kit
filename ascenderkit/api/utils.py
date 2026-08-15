import logging
import re

log = logging.getLogger(__name__)

descRE = re.compile(r'^[*] `(\w+)`: [^(]*\((\w+), ([^)]+)\)')


def freeze(key):
    if key is None:
        return None
    return frozenset((k, freeze(v) if isinstance(v, dict) else v) for k, v in key.items())


def parse_description(desc):
    options = {}
    desc_lines = []
    if 'POST' in desc:
        desc_lines = desc[desc.index('POST') :].splitlines()
    else:
        desc_lines = desc.splitlines()
    for line in desc_lines:
        match = descRE.match(line)
        if not match:
            continue
        options[match.group(1)] = {'type': match.group(2), 'required': match.group(3) == 'required'}
    return options


def remove_encrypted(value):
    if value == '$encrypted$':
        return ''
    if isinstance(value, list):
        return [remove_encrypted(item) for item in value]
    if isinstance(value, dict):
        return {k: remove_encrypted(v) for k, v in value.items()}
    return value


def drop_encrypted(value):
    """Strip ``$encrypted$`` placeholders out of an import payload entirely.

    An export writes ``$encrypted$`` wherever the server refused to disclose a
    secret. The server reads that same token back as "keep the value you
    already have", so it is only meaningful when the object exists. When one is
    being created there is nothing to keep, and sending the placeholder would
    store it verbatim as the secret.

    Removing the key instead of blanking it leaves the field unset, so the
    server applies its own default and callers can supply one of their own.

    Args:
        value: A payload fragment: a dict, a list, or a scalar.

    Returns:
        The same structure with every ``$encrypted$`` entry removed.
    """
    if isinstance(value, dict):
        return {k: drop_encrypted(v) for k, v in value.items() if v != '$encrypted$'}
    if isinstance(value, list):
        return [drop_encrypted(item) for item in value if item != '$encrypted$']
    return value


def get_post_fields(page, cache):
    options_page = cache.get_options(page)
    if options_page is None:
        return None

    if 'POST' not in options_page.r.headers.get('Allow', ''):
        return None

    if 'POST' in options_page.json['actions']:
        return options_page.json['actions']['POST']
    else:
        log.warning("Insufficient privileges on %s, inferring POST fields from description.", options_page.endpoint)
        return parse_description(options_page.json['description'])
