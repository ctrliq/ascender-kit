from typing import Any

from contextlib import suppress

import ascenderkit.exceptions as exc


class HasInstanceGroups(object):
    # Supplied by the Page this is mixed into: response-body fields arrive
    # through Page.__getattr__, the rest are Page's own. Annotations rather
    # than assignments, so nothing is created at runtime.
    related: Any

    def add_instance_group(self, instance_group):
        with suppress(exc.NoContent):
            self.related['instance_groups'].post(dict(id=instance_group.id))

    def remove_instance_group(self, instance_group):
        with suppress(exc.NoContent):
            self.related['instance_groups'].post(dict(id=instance_group.id, disassociate=instance_group.id))

    def remove_all_instance_groups(self):
        for ig in self.related.instance_groups.get().results:
            self.remove_instance_group(ig)
