# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 25.x    | :white_check_mark: |
| < 25.0  | :x:                |

Ascender Kit tracks the versioning of [Ascender](https://github.com/ctrliq/ascender)
itself, and only the most recent release line receives security fixes.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly. **Do not open a public GitHub issue for security vulnerabilities.**

Instead, please send an email to **security@ctrliq.com** with:

- A description of the vulnerability
- Steps to reproduce the issue
- Any potential impact

You should receive a response within 72 hours acknowledging receipt. We will
work with you to understand the issue and coordinate a fix and disclosure
timeline.

## Disclosure Policy

We follow coordinated disclosure. We ask that you give us a reasonable amount
of time to address the issue before making any information public.

## Credentials and tokens

Ascender Kit reads credentials from environment variables, from `--conf.*`
command line arguments, and from a credential file. Be aware that:

- Command line arguments are visible to other users via the process list.
- Prefer environment variables or `ascender login` tokens.
- `ascender login -f human` prints a token to standard output for shell use.
- Treat that token like a password, and revoke it if it leaks.
- `-k` and `--conf.insecure` disable TLS certificate verification.
- Never use them against a production server.

## TLS verification when used as a library

The `ascender` command verifies TLS certificates unless you pass `-k`.

The Python library does not. `config.assume_untrusted` defaults to `True`, and
the connection verifies certificates only when it is `False`, so importing
`ascenderkit` and driving the API directly talks to the server without checking
its certificate:

```python
from ascenderkit import api, config

config.base_url = 'https://ascender.example.org'
config.assume_untrusted = False   # verify certificates; not the default
root = api.Api()
```

The default comes from this code's origins as a test toolkit, where pointing at
a throwaway server with a self-signed certificate is the normal case. Set
`assume_untrusted` to `False` for anything else.
