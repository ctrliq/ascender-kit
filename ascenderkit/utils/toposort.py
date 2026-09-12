"""Topological sort, backed by the standard library's `graphlib`.

`has_create.creation_order` consumes the batched form this returns: a list of
sets, where every item in a set can be created once the preceding sets exist.
"""

from graphlib import CycleError, TopologicalSorter

__all__ = ['toposort', 'CircularDependencyError']


class CircularDependencyError(ValueError):
    """Raised when the dependency graph cannot be ordered.

    :param cycle: the nodes `graphlib` found in the cycle, first node repeated
        last, which is the shape `CycleError` reports.
    """

    def __init__(self, cycle):
        super().__init__('Circular dependencies exist among these items: {}'.format(' -> '.join(repr(node) for node in cycle)))
        self.data = cycle


def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependences, each subsequent set consists of items that depend upon
    items in the preceding sets."""
    # Self dependencies are dropped rather than reported. graphlib treats an
    # item depending on itself as a one-node cycle, where a page listing itself
    # among its own dependencies is meaningless rather than an error.
    graph = {item: set(dependencies) - {item} for item, dependencies in data.items()}

    sorter = TopologicalSorter(graph)
    try:
        sorter.prepare()
    except CycleError as e:
        raise CircularDependencyError(e.args[1]) from None

    while sorter.is_active():
        group = sorter.get_ready()
        yield set(group)
        sorter.done(*group)
