# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to the versioning of
[Ascender](https://github.com/ctrliq/ascender) itself.

## [Unreleased]

## [25.5.1] - 2026-08-17

### Added

- Standalone repository for the Ascender command line client, previously
  distributed from within the main Ascender repository.
- `-h` is now accepted as a short form of `--help`, and resource-level help
  (`ascender users --help`) prints the list of actions for that resource.
  Ported from [ansible/awx#16307](https://github.com/ansible/awx/pull/16307),
  minus its early exit out of argument parsing: the resource list is discovered
  from the server and is the substance of `ascender --help`, so skipping the
  connection to save a round trip empties the output it exists to produce.
  Unreachable servers already fall back to the global help.
- Monitored jobs that end up `canceled` now exit with return code 2, so scripts
  can tell a cancellation from a failure (which stays at 1). Ported from
  [ansible/awx#15678](https://github.com/ansible/awx/pull/15678).

### Changed

- **Breaking:** the distribution is now published as `ascender-kit` rather than
  `awxkit`. Install with `pip install ascender-kit`.
- **Breaking:** the importable module is now `ascenderkit` rather than `awxkit`.
  Update imports from `from awxkit import ...` to `from ascenderkit import ...`.
- **Breaking:** the command line entry point is now `ascender` rather than `awx`.
- **Breaking:** the interactive session entry point is now `ascender-shell`
  rather than `akit`.
- **Breaking:** the `AWXKIT_*` environment variables are now named
  `ASCENDERKIT_*`. This affects `ASCENDERKIT_BASE_URL`,
  `ASCENDERKIT_CREDENTIAL_FILE`, `ASCENDERKIT_PROJECT_FILE`,
  `ASCENDERKIT_CLIENT_CONNECTION_ATTEMPTS`, `ASCENDERKIT_PREVENT_TEARDOWN`,
  `ASCENDERKIT_SESSIONS`, `ASCENDERKIT_API_BASE_PATH`, `ASCENDERKIT_DEBUG`,
  `ASCENDERKIT_USER` and `ASCENDERKIT_USER_PASSWORD`. The old names are no
  longer read, so an unmigrated variable is silently ignored rather than
  reported as an error.
- **Breaking:** `awxkit.exceptions.UnexpectedAWXState` is now
  `ascenderkit.exceptions.UnexpectedAscenderState`.
- **Breaking:** the `Config.is_awx_license` property is now
  `Config.is_ascender_license`.
- The default execution environment image used when creating an execution
  environment is now `ghcr.io/ctrliq/ascender-ee:latest`, matching the Ascender
  server default, rather than `quay.io/ansible/awx-ee:latest`.
- `HelpfulArgumentParser` no longer strips `-h` and `--help` out of the argument
  list before parsing. That workaround existed because the CLI had no real help
  action; it now does, and argparse handles the flags. Upstream removed the same
  override in [ansible/awx#15692](https://github.com/ansible/awx/pull/15692).
- The `CONTROLLER_*` and `TOWER_*` environment variables are unchanged, as are
  the `awx_sessionid` session cookie name and the `/tmp/awx_<id>` job folder
  prefix, which are part of the wire contract with the Ascender server.

### Fixed

- Human-readable output (`-f human`) no longer crashes on numeric fields under
  Python 3.12 and newer. `locale.format()` was removed in Python 3.12 and has
  been replaced with `locale.format_string()`.
- Wrapping an exception in an `ascenderkit.exceptions.Common` subclass no longer
  raises `TypeError: argument after * must be an iterable`.
- `ascender import` updates existing users with PATCH instead of PUT. PUT
  dropped every field the export did not carry, including the password. Ported
  from [ansible/awx#14053](https://github.com/ansible/awx/pull/14053).
- `ascender import` no longer crashes on a role whose `content_object` is
  present but null. Ported from
  [ansible/awx#15128](https://github.com/ansible/awx/pull/15128), and applied to
  `_assign_role` as well, which upstream has not fixed.
- `modify` now advertises its fields for users who hold PUT on the detail
  endpoint without POST on the list endpoint, instead of showing none. Ported
  from [ansible/awx#16276](https://github.com/ansible/awx/pull/16276).
- `import ascenderkit` works on a clean install. `packaging` backs
  `ascenderkit.ascender.version_cmp`, which the package imports unconditionally,
  and `urllib3` is imported directly by the CLI; neither was declared, so both
  only happened to be present when another package pulled them in. `setuptools`
  is no longer required, as nothing imports it at runtime.
- `pip install ascender-kit` no longer installs a top-level `tests` package next
  to `ascenderkit`. The exclusion passed to `find_packages` still named the
  `test` directory the client used before the move, so this repository's `tests`
  tree was collected as a package and the wheel declared it in `top_level.txt`,
  where it shadowed any other `tests` package on the path. The source
  distribution still carries the tests, through `MANIFEST.in`.
- Building the CLI documentation produces pages again. The Sphinx plugin builds
  the argument parser purely in order to document it, and the new early exit for
  `ascender --help` terminated the build part-way through. Because it exits zero,
  the build reported success while writing no HTML at all.
- The `ascender` credential kind resolves to the same place in both lookup
  paths. `cloud_types` still listed `tower` after the rebrand, so
  `config_cred_from_kind` looked under `credentials.ascender` while
  `get_credential_type_and_config_cred` looked under `credentials.cloud.ascender`.
- `ascender import` no longer destroys credential secrets. An export writes
  `$encrypted$` wherever the server withheld a secret, and the server reads that
  same token back as "keep the value you already have". The client was rewriting
  it to an empty string first, so importing an export overwrote every secret in
  it with a blank. Placeholders are now passed through when updating an existing
  object, and dropped when creating one, where there is nothing to preserve.
- `ascender import` no longer fails with
  `{'password': ['This field may not be blank.']}` on any exported user, which
  made an unedited export un-importable. Same cause as above.
- A user created by `ascender import` now receives the documented `abc123`
  default password. `post_data.setdefault('password', 'abc123')` could never
  fire, because the blanking above meant the key was always already present.
- The `settings` resource works for users who may not change settings. Building
  the `modify` action read `actions['PUT']` out of the endpoint's OPTIONS
  without checking it was there; a user without permission is served no PUT
  section, so it raised `KeyError: 'PUT'`. That happens while the parser is
  built, before any action runs, so it took the whole resource down with it and
  even the read-only `settings list` could not run. Such a user is now offered
  no settable keys, and the other actions behave normally.
- `ASCENDERKIT_PROJECT_FILE` is read. The variable was checked against the
  environment but its value was then looked up in `config`, which never holds
  it, so `load_projects` received None, took that for "no file given", and
  answered `{}`. The file named by the variable was never opened, and naming one
  that does not exist reported nothing.
- `ascenderkit.utils.args_string_to_list()` works. Every non-empty input raised
  `AttributeError: 'str' object has no attribute 'decode'`, a Python 2 leftover
  that only the empty string escaped by never entering the loop. It backs the
  `job_args` property on jobs, which parses shell argument strings.
- `ascender-shell --non-interactive` does what it says. The flag was accepted
  and advertised, but nothing read it, so the session always ended at an
  interactive prompt: `ascender-shell -x -f script.py` ran the script and then
  sat waiting for input instead of finishing.
- Reading a `@file` argument no longer leaks the file handle. `--extra_vars
  @vars.yml`, its nested top-level `@path` values, and the `--file` script for
  `ascender-shell` all read through a context manager now, so they no longer
  raise ResourceWarning under `python -X dev`.
- The traceback printed under `-v` goes to stderr instead of into the middle of
  the output document. The stream was passed to `print` as a value rather than
  as its `file`, so an API error wrote the traceback, followed by a repr of the
  stderr object, onto stdout ahead of the JSON or YAML being parsed there.
- `ascender export` now says so when a named selector matches nothing, e.g.
  `export --users alcie`. It exported `{"users": []}` and exited 0, which is
  indistinguishable from a successful export, so a mistyped name produced an
  empty backup with nothing to suggest anything had gone wrong. The warning goes
  to stderr; the exported document and the exit status are unchanged.
- A successful `ascender export` no longer prints `Unable to construct a natural
  key for 'webhook_key' of object /api/v2/projects/1/, skipping.` to stderr, for
  that field and every other write-only related field the server advertises as a
  POST field. Skipping such a field is the expected outcome rather than an
  export problem, so it is logged at debug level and surfaces under `--verbose`
  alongside the rest of the export trace.
- Resource-level help works whatever precedes it. `ascender -k users --help`
  printed an empty action list and exited 2 with
  `the following arguments are required: action`. Two faults met there: options
  taking no value, such as `-k` and `-v`, consumed the token after them, so the
  resource name was read as an option's value; and the help was printed before
  the actions had been registered, so it had nothing to list. Which options take
  a value is now read off the parser instead of assumed, and the help is printed
  once the actions exist. Every help form now exits 0.
- The resource is read from the arguments the client was given rather than from
  `sys.argv`. The two are the same list when the CLI is run from a terminal and
  are not when it is driven in process, so `run(argv=[...])` and
  `cli.parse_args([...])` resolved the resource out of whatever arguments the
  host program happened to be started with.
- `ascender host_metrics list` works again. The page class overrode `get()`
  without carrying over the `all_pages` argument, so a client-side flag was
  forwarded to the server as a query parameter and came back as
  `HostMetric has no field named 'all_pages'`. The `metrics` and `bulk` pages
  carried the same defect without a caller that triggered it. All three now
  declare the JSON `Accept` header they wanted instead of reimplementing `get`.
- The fallback that prints the global help when the server cannot be reached no
  longer depends on `argv[0]` matching the literal string `ascender`, which it
  never does when the console script is invoked by absolute path.
- Launching a system job template reports the real problem when the launched job
  cannot be found afterwards. The message built for that case read
  `result.json['job']`, a key the launch response does not carry — it answers
  with `system_job` — so the diagnostic raised `KeyError: 'job'` and hid the
  condition it was written to describe.

### Security

- `ascender import -f yaml` parses its input with `yaml.safe_load()`. It read
  stdin through the loader that implements the `!include` and `!import` tags,
  which resolve to local files relative to the working directory, so an export
  file from an untrusted source could pull local file contents into the payload
  sent to the server. Those tags were never part of the export format.

- License and duplicate-detection checks match with plain substring tests rather
  than `.*`-wrapped regular expressions evaluated against whole response bodies,
  removing the ReDoS exposure those patterns carried. Ported from
  [ansible/awx#16503](https://github.com/ansible/awx/pull/16503).
