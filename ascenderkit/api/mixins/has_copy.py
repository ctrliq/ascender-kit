from typing import Any, Callable

from ascenderkit.api.pages import Page
from ascenderkit.utils import PseudoNamespace, random_title


class HasCopy(object):
    # Supplied by the Page this is mixed into: response-body fields arrive
    # through Page.__getattr__, the rest are Page's own. Annotations rather
    # than assignments, so nothing is created at runtime.
    json: PseudoNamespace
    connection: Any
    get_related: Callable[..., Any]

    def can_copy(self):
        return self.get_related('copy').can_copy

    def copy(self, name=''):
        """Return a copy of current page"""
        payload = {"name": name or "Copy - " + random_title()}
        endpoint = self.json.related['copy']
        page = Page(self.connection, endpoint=endpoint)
        return page.post(payload)
