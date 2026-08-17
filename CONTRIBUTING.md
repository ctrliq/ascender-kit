# Contributing to Ascender Kit

Thanks for your interest in contributing to `ascender-kit`. This document covers
the development setup, testing, and PR guidelines.

## Development setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/<your-user>/ascender-kit.git
   cd ascender-kit
   ```

2. Create a virtual environment and install the package in editable mode with
   the optional extras:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[websockets,formatting,crypto]"
   ```

3. Install the development dependencies:

   ```bash
   pip install black flake8 pytest pytest-mock coverage tox
   ```

Most of the test suite runs against mocks and needs no server. To exercise the
CLI by hand you will want a running [Ascender](https://github.com/ctrliq/ascender)
instance to point at.

## Running tests

### Unit tests

These need nothing but the package itself.

```bash
pytest tests/unit -v
```

### Integration tests

These drive the CLI against a real server, and are skipped unless you point
them at one. They cover what unit tests cannot: that an export survives being
imported back, that monitored jobs exit 0, 1 and 2 for success, failure and
cancellation, and that token authentication works.

```bash
export CONTROLLER_HOST=https://ascender.example.org
export CONTROLLER_USERNAME=admin CONTROLLER_PASSWORD=...
export CONTROLLER_VERIFY_SSL=false        # self-signed development servers
pytest tests/integration -v
```

They write to the server they are given, so use a development instance rather
than anything you care about. Expect a couple of minutes: most of it is the
sweep across every resource, two full export/import round trips, and launching
real jobs to watch them finish.

With `pytest-xdist` installed they can be spread across workers, which cuts
roughly a third off the wall clock:

```bash
pytest tests/integration -n 4 --dist loadfile
```

`--dist loadfile` matters: it keeps each file on a single worker, so the tests
within one file still run in order. They all share one server, though, so this
is a speed-up rather than isolation — the import tests are writing while the
others read. It has been stable in practice, but a sequential run is the one to
trust when something looks odd.

### Linting

```bash
black --check ascenderkit tests setup.py
flake8 ascenderkit
```

### Everything at once

```bash
tox
```

`tox` runs the `lint` and `test` environments, which is the same set of checks
CI runs on every pull request.

## Making changes

### Branching

Create a feature branch from `main`:

```bash
git checkout -b my-feature main
```

### Code style

- Formatting is enforced by `black`, configured in `pyproject.toml` with a
  160-character line limit and string normalization disabled. Run `black
  ascenderkit tests setup.py` before committing.
- `flake8` settings live in `tox.ini`. The selected checks are deliberately
  narrow, matching the main Ascender repository.
- New API pages belong in `ascenderkit/api/pages/` and must be registered with
  `page.register_page()` so the client can resolve them from an endpoint.
- New CLI behaviour that is not simply discovered from the API belongs in
  `ascenderkit/cli/resource.py` as a custom command.

### Values that must not be renamed

A few string literals are part of the wire contract with the Ascender server
rather than branding, and changing them will break the client against a real
installation. They are marked with comments in the source:

| Value | Mirrors |
|---|---|
| `awx_sessionid` in `ascenderkit/ws.py` | `SESSION_COOKIE_NAME` in `awx/settings/defaults.py` |
| `/tmp/awx_{id}` in `ascenderkit/api/pages/unified_jobs.py` | `JOB_FOLDER_PREFIX` in `awx/main/constants.py` |

If either changes upstream in [ctrliq/ascender](https://github.com/ctrliq/ascender),
it has to change here in the same release.

### Changelog

Every PR that changes user-facing behaviour needs an entry in
[CHANGELOG.md](CHANGELOG.md) under the `Unreleased` heading. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); pick the appropriate
category:

| Category | When to use |
|---|---|
| `Added` | New features |
| `Changed` | Changes to existing behaviour |
| `Deprecated` | Features marked for future removal |
| `Removed` | Previously deprecated features now removed |
| `Fixed` | Bug fixes |
| `Security` | Vulnerability fixes |

### Commit messages

Write clear, concise commit messages:

```
Short summary (under 72 characters)

Longer description of what changed and why, if needed.
```

## Submitting a PR

1. Make sure the tests and linters pass locally (`tox`).
2. Add a changelog entry if the change is user-facing.
3. One logical change per PR — don't bundle unrelated fixes.
4. Target the `main` branch.
5. Fill in the PR template (summary, type of change, component, checklist).

CI runs automatically on every PR: linting, and the unit tests on the oldest
and newest supported Python versions. Version-specific breakage lives at the
boundaries of the supported range, so testing both ends covers it without
running an interpreter for every version in between.

## Reporting issues

Open an issue at
[github.com/ctrliq/ascender-kit/issues](https://github.com/ctrliq/ascender-kit/issues).
Include the Ascender Kit version (`ascender --version`), the Python version, the
Ascender server version, and the command that reproduces the problem along with
its output at `-v`.

For security vulnerabilities, follow [SECURITY.md](SECURITY.md) instead.
