"""Version resolution only. Every other piece of packaging metadata lives in
pyproject.toml, as PEP 621 `[project]` fields.

setuptools_scm derives the version from the git tags, which is how releases are
cut. A VERSION file beside this one wins when it is present, which is the escape
hatch for building from a source archive carrying neither a `.git` directory nor
the PKG-INFO an sdist would have.
"""

import os

from setuptools import setup


def version_file():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')
    return path if os.path.exists(path) else None


_version_file = version_file()

if _version_file:
    with open(_version_file) as f:
        setup(version=f.read().strip())
else:
    # The package sits at the root of its own repository, so setuptools_scm
    # reads the tags from here rather than from a parent checkout.
    setup(use_scm_version=dict(root='.', relative_to=__file__))
