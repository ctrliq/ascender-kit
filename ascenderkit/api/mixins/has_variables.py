import yaml

from ascenderkit.utils import PseudoNamespace


class HasVariables(object):
    # Supplied by the Page this is mixed into: response-body fields arrive
    # through Page.__getattr__, the rest are Page's own. Annotations rather
    # than assignments, so nothing is created at runtime.
    json: PseudoNamespace

    @property
    def variables(self):
        return PseudoNamespace(yaml.safe_load(self.json.variables))
