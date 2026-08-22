# Ascender Kit

[![CI](https://github.com/ctrliq/ascender-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/ctrliq/ascender-kit/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-ascender--kit-blue.svg)](https://pypi.org/project/ascender-kit/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/)

Ascender Kit provides `ascender`, the official command line client for [Ascender](https://github.com/ctrliq/ascender), along with the Python library that backs it. Rather than hard-coding a list of commands, the CLI discovers what your server supports at runtime by issuing HTTP OPTIONS requests against the REST API, so the resources and arguments you see are the ones your Ascender version actually offers.

## Requirements

- Python 3.11 or newer

## Installation

### From PyPI

```bash
pip install ascender-kit
```

Some capabilities are kept behind extras so the base install stays small:

```bash
pip install ascender-kit[websockets]   # job output streaming
pip install ascender-kit[formatting]   # jq-style filtering of JSON output
pip install ascender-kit[crypto]       # encrypted credential support
```

### From source

```bash
git clone https://github.com/ctrliq/ascender-kit.git
pip install -e ascender-kit
```

## Using the client

Point the client at your server and confirm it can authenticate:

```bash
export CONTROLLER_HOST=https://ascender.example.org
export CONTROLLER_USERNAME=alice
export CONTROLLER_PASSWORD=secret

ascender config
```

Because the command set is discovered from the server, `--help` is the reference:

```bash
ascender --help                      # every available resource
ascender job_templates --help        # every action on job templates
ascender job_templates launch --help # every argument for one action
```

A few common operations:

```bash
ascender jobs list -f human --filter name,created,status
ascender job_templates launch 'Example Job Template' --monitor -f human
ascender export > resources.json
```

## Authentication

Connection settings resolve from highest to lowest precedence:

| Precedence | Source |
| ---------- | ------ |
| 1 | Command line flags, such as `--conf.host` and `--conf.token` |
| 2 | Environment variables: `CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD` |
| 3 | The config file written by `ascender login` and `ascender config` |

For repeated use, generate a token instead of passing credentials each time:

```bash
$(ascender login -f human)
```

## Included content

- **`ascender` CLI**: the command line client, with resources discovered at runtime
- **`ascenderkit` library**: the same API client, importable for your own tooling
- **Output formats**: JSON by default, plus YAML and human-readable tables via `-f`
- **Field filtering**: narrow output to the columns you care about with `--filter`
- **Job monitoring**: follow job output over a websocket with `--monitor`
- **Import and export**: move resources between servers with `export` and `import`

## Testing

Ascender Kit uses tox to manage test environments.

- **Full suite**: `tox`
- **Tests only**: `tox -e test`
- **Lint only**: `tox -e lint`

## Documentation

- CLI documentation lives in [`ascenderkit/cli/docs`](./ascenderkit/cli/docs)
- Product documentation is at [docs.ascender-automation.org](https://docs.ascender-automation.org)

## The Ascender ecosystem

| Repository | Description |
| ---------- | ----------- |
| [ascender](https://github.com/ctrliq/ascender) | The platform itself: web UI, REST API, and task engine |
| [ascender-install](https://github.com/ctrliq/ascender-install) | Installer for Ascender and Ledger, with Galaxy Proxy support |
| [ascender-k8s-install](https://github.com/ctrliq/ascender-k8s-install) | Kubernetes installer for Ascender, Ledger, and React |
| [ascender-pro-install](https://github.com/ctrliq/ascender-pro-install) | Enhanced installer adding Reaqt, Registry, and Galaxy Proxy |
| [ascender-operator](https://github.com/ctrliq/ascender-operator) | Kubernetes operator that deploys and manages Ascender |
| [ascender-ee](https://github.com/ctrliq/ascender-ee) | Default execution environment image for Ascender jobs |
| [ascender-kit](https://github.com/ctrliq/ascender-kit) | The `ascender` command line client and Python API library |
| [ascender-collection](https://github.com/ctrliq/ascender-collection) | The `ctrliq.ascender` Ansible collection for a controller |
| [ascender-ledger](https://github.com/ctrliq/ascender-ledger) | Reporting tool for host facts and playbook changes |
| [ascender-galaxy-proxy](https://github.com/ctrliq/ascender-galaxy-proxy) | Caching proxy for Ansible Galaxy collection downloads |
| [ascender-playbooks](https://github.com/ctrliq/ascender-playbooks) | Example playbooks for use with Ascender |
## Contributing

- See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, testing, and pull requests.
- Report bugs and feature ideas via [GitHub Issues](https://github.com/ctrliq/ascender-kit/issues).
- For security vulnerabilities, follow [SECURITY.md](./SECURITY.md) rather than opening an issue.
- Join the [Ascender forum](https://forum.ascender-automation.org) to discuss development topics.

## License

Licensed under the **Apache License 2.0**. See [LICENSE](./LICENSE) and [NOTICE.txt](./NOTICE.txt).
