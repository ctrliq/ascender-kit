# Ascender Kit

Ascender Kit provides `ascender`, the official command line client for [Ascender](https://github.com/ctrliq/ascender), along with the Python library that backs it.

Rather than hard-coding a list of commands, the CLI discovers what your server supports at runtime by issuing HTTP OPTIONS requests against the Ascender REST API. The set of resources, actions, and arguments you see is therefore the set your particular Ascender version actually offers.

Features
--------

- **Runtime API discovery** — resources and their arguments come from the server, not a hard-coded table
- **Consistent output formats** — JSON by default, with YAML and human-readable tables via `-f`
- **Field filtering** — narrow output to the columns you care about with `--filter`
- **Token-based authentication** — generate and store OAuth2.0 tokens with `ascender login`
- **Job monitoring** — follow job output as it is produced with `--monitor` or `--wait`
- **Import and export** — move resources between servers with `ascender export` and `ascender import`
- **Python library** — the same API client is importable as `ascenderkit` for use in your own tooling

Installation
------------

    pip install ascender-kit

Some capabilities are kept behind optional extras so the base install stays small:

    pip install ascender-kit[websockets]   # WSClient, the library's live event stream
    pip install ascender-kit[formatting]   # jq-style filtering of JSON output
    pip install ascender-kit[crypto]       # encrypted credential support

Ascender Kit requires Python 3.11 or newer.

Getting Started
---------------

Point the client at your server and confirm it can authenticate:

    export CONTROLLER_HOST=https://ascender.example.org
    export CONTROLLER_USERNAME=alice
    export CONTROLLER_PASSWORD=secret

    ascender config

Because the command set is discovered from the server, `--help` is the reference:

    ascender --help                      # every available resource
    ascender job_templates --help        # every action on job templates
    ascender job_templates launch --help # every argument for one action

A few common operations:

    ascender jobs list -f human --filter name,created,status
    ascender job_templates launch 'Example Job Template' --monitor -f human
    ascender export > resources.json

For repeated use, generate a token instead of passing credentials each time:

    $(ascender login -f human)

Documentation
-------------

- Full CLI documentation lives in [`ascenderkit/cli/docs`](https://github.com/ctrliq/ascender-kit/tree/main/ascenderkit/cli/docs) and covers usage, authentication, output formats, and worked examples.
- Ascender documentation is available at [Ascender Documentation](https://docs.ascender-automation.org).

Contributing
------------

- See [CONTRIBUTING.md](https://github.com/ctrliq/ascender-kit/blob/main/CONTRIBUTING.md) for development setup, testing, and pull request guidelines.
- Join us on our [forum](https://forum.ascender-automation.org) to discuss development topics.

Reporting Issues
----------------

- If you're experiencing a problem that you feel is a bug in Ascender Kit, or have ideas for improving it, we encourage you to open a GitHub issue and share your feedback.
- For security vulnerabilities, please follow the process in [SECURITY.md](https://github.com/ctrliq/ascender-kit/blob/main/SECURITY.md) rather than opening a public issue.

License
-------

Apache License 2.0. See [LICENSE](https://github.com/ctrliq/ascender-kit/blob/main/LICENSE) and [NOTICE.txt](https://github.com/ctrliq/ascender-kit/blob/main/NOTICE.txt).
