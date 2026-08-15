from __future__ import print_function

import logging
import os
import sys
from importlib.metadata import version as _get_version

from requests.exceptions import RequestException

from .custom import handle_custom_actions
from .format import add_authentication_arguments, add_output_formatting_arguments, FORMATTERS, format_response
from .options import ResourceOptionsParser, UNIQUENESS_RULES
from .resource import parse_resource, is_control_resource
from ascenderkit import api, config, utils, exceptions, WSClient  # noqa
from ascenderkit.cli.utils import HelpfulArgumentParser, cprint, disable_color, colored
from ascenderkit.ascender.utils import uses_sessions  # noqa

# The distribution is named ascender-kit; the importable module is ascenderkit.
__version__ = _get_version('ascender-kit')


class CLI(object):
    """A programmatic HTTP OPTIONS-based CLI for Ascender.

    This CLI works by:

    - Configuring CLI options via Python's argparse (authentication, formatting
      options, etc...)
    - Discovering Ascender API endpoints at /api/v2/ and mapping them to _resources_
    - Discovering HTTP OPTIONS _actions_ on resources to determine how
      resources can be interacted with (e.g., list, modify, delete, etc...)
    - Parsing sys.argv to map CLI arguments and flags to
      ascenderkit SDK calls

    ~ ascender <resource> <action> --parameters

    e.g.,

    ~ ascender users list -v
    GET /api/ HTTP/1.1" 200
    GET /api/v2/ HTTP/1.1" 200
    POST /api/login/ HTTP/1.1" 302
    OPTIONS /api/v2/users/ HTTP/1.1" 200
    GET /api/v2/users/
    {
     "count": 2,
     "results": [
     ...

    Interacting with this class generally involves a few critical methods:

    1.  parse_args() - this method is used to configure and parse global CLI
        flags, such as formatting flags, and arguments which represent client
        configuration (including authentication details)
    2.  connect() - once configuration is parsed, this method fetches /api/v2/
        and itemizes the list of supported resources
    3.  parse_resource() - attempts to parse the <resource> specified on the
        command line (e.g., users, organizations), including logic
        for discovering available actions for endpoints using HTTP OPTIONS
        requests

    At multiple stages of this process, an internal argparse.ArgumentParser()
    is progressively built and parsed based on sys.argv, (meaning, that if you
    supply invalid or incomplete arguments, argparse will print the usage
    message and an explanation of what you got wrong).
    """

    subparsers = {}
    original_action = None

    def __init__(self, stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin):
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.verbose = False

    def get_config(self, key):
        """Helper method for looking up the value of a --conf.xyz flag"""
        return getattr(self.args, 'conf.{}'.format(key))

    @property
    def help(self):
        return '--help' in self.argv or '-h' in self.argv

    def _option_takes_a_value(self, arg):
        """Whether `arg` consumes the token after it.

        Ask the parser rather than guessing. Flags such as -k, -v and --help
        take no value, so the token after them is a resource or an action, not
        something they swallow. The parser is not built yet on some code paths,
        and there the old assumption that every option takes a value stands.
        """
        parser = getattr(self, 'parser', None)
        if parser is None:
            return True
        for action in parser._actions:
            if arg in action.option_strings:
                return action.nargs != 0
        return True

    def _get_non_option_args(self, before_help=False):
        """Extract non-option arguments from argv, optionally only those before help flag."""
        if before_help and self.help:
            # Find position of help flag
            help_pos = next((i for i, arg in enumerate(self.argv) if arg in ('--help', '-h')), len(self.argv))
            args_to_check = self.argv[:help_pos]
        else:
            args_to_check = self.argv

        # argv[0] is the program name and is never a resource or an action.
        # Drop it by position rather than by matching a literal, because when
        # installed as a console script it arrives as a full path.
        args_to_check = args_to_check[1:]

        non_option_args = []
        i = 0
        while i < len(args_to_check):
            arg = args_to_check[i]

            if arg.startswith('-'):
                # This is an option
                if '=' in arg:
                    # Long option with value: --opt=val
                    i += 1
                else:
                    # Option without embedded value: --opt or -o
                    i += 1
                    # Only consume the next argument when this option actually
                    # takes one, and it is not itself an option.
                    if self._option_takes_a_value(arg) and i < len(args_to_check) and not args_to_check[i].startswith('-'):
                        i += 1
            else:
                # This is a positional argument
                non_option_args.append(arg)
                i += 1

        return non_option_args

    def _is_main_help_request(self):
        """
        Determine if help request is for the main CLI (`ascender --help`) rather
        than a subcommand (`ascender users create --help`).

        Returns True if this is a main CLI help request that should exit early.
        """
        if not self.help:
            return False

        # If there are non-option arguments before help flag, this is subcommand help
        return len(self._get_non_option_args(before_help=True)) == 0

    def authenticate(self):
        """Configure the current session (or OAuth2.0 token)"""
        token = self.get_config('token')
        if token:
            self.root.connection.login(
                None,
                None,
                token=token,
            )
        else:
            config.use_sessions = True
            self.root.load_session().get()

    def connect(self):
        """Fetch top-level resources from /api/v2"""
        config.base_url = self.get_config('host')
        config.client_connection_attempts = 1
        config.assume_untrusted = False
        if self.get_config('insecure'):
            config.assume_untrusted = True

        config.credentials = utils.PseudoNamespace(
            {
                'default': {
                    'username': self.get_config('username'),
                    'password': self.get_config('password'),
                }
            }
        )

        _, remainder = self.parser.parse_known_args()
        if remainder and remainder[0] == 'config':
            # the config command is special; it doesn't require
            # API connectivity
            return
        # ...otherwise, set up an ascenderkit connection because we're
        # likely about to do some requests to /api/v2/
        self.root = api.Api()
        try:
            self.fetch_version_root()
        except RequestException:
            # If we can't reach the API root (this usually means that the
            # hostname is wrong, or the credentials are wrong) then a bare
            # `ascender --help` should still print the global help rather than
            # an error. Anything more specific than that needs the server, so
            # the caller gets the exception.
            if self._is_main_help_request():
                return
            raise

    def fetch_version_root(self):
        try:
            self.v2 = self.root.get().available_versions.v2.get()
        except AttributeError:
            raise RuntimeError('An error occurred while fetching {}/api/'.format(self.get_config('host')))

    def parse_resource(self, skip_deprecated=False):
        """Attempt to parse the <resource> (e.g., jobs) specified on the CLI

        If a valid resource is discovered, the user will be authenticated
        (either via an OAuth2.0 token or session-based auth) and the remaining
        CLI arguments will be processed (to determine the requested action
        e.g., list, create, delete)

        :param skip_deprecated: when False (the default), deprecated resource
                                names from the open source tower-cli project
                                will be allowed
        """
        self.resource = parse_resource(self, skip_deprecated=skip_deprecated)
        if self.resource:
            self.authenticate()
            resource = getattr(self.v2, self.resource)
            if is_control_resource(self.resource):
                # control resources are special endpoints that you can only
                # do an HTTP GET to, and which return plain JSON metadata
                # examples are `/api/v2/ping/`, `/api/v2/config/`, etc...
                if self.help:
                    self.subparsers[self.resource].print_help()
                    raise SystemExit()
                self.method = 'get'
                response = getattr(resource, self.method)()
            else:
                response = self.parse_action(resource)

            _filter = self.get_config('filter')

            # human format for metrics, settings is special
            if self.resource in ('metrics', 'settings') and self.get_config('format') == 'human':
                response.json = {'count': len(response.json), 'results': [{'key': k, 'value': v} for k, v in response.json.items()]}
                _filter = 'key, value'

            if self.get_config('format') == 'human' and _filter == '.' and self.resource in UNIQUENESS_RULES:
                _filter = ', '.join(UNIQUENESS_RULES[self.resource])

            formatted = format_response(
                response, fmt=self.get_config('format'), filter=_filter, changed=self.original_action in ('modify', 'create', 'associate', 'disassociate')
            )
            if formatted:
                print(utils.to_str(formatted), file=self.stdout)
            if hasattr(response, 'rc'):
                raise SystemExit(response.rc)
        else:
            self.parser.print_help()

    def parse_action(self, page, from_sphinx=False):
        """Perform an HTTP OPTIONS request

        This method performs an HTTP OPTIONS request to build a list of valid
        actions, and (if provided) runs the code for the action specified on
        the CLI

        :param page: a ascenderkit.api.pages.TentativePage object representing the
                     top-level resource in question (e.g., /api/v2/jobs)
        :param from_sphinx: a flag specified by our sphinx plugin, which allows
                            us to walk API OPTIONS using this function
                            _without_ triggering a SystemExit (argparse's
                            behavior if required arguments are missing)
        """
        subparsers = self.subparsers[self.resource].add_subparsers(dest='action', metavar='action')
        subparsers.required = True

        # parse the action from OPTIONS
        parser = ResourceOptionsParser(self.v2, page, self.resource, subparsers)
        if parser.deprecated:
            description = 'This resource has been deprecated and will be removed in a future release.'
            if not from_sphinx:
                description = colored(description, 'yellow')
            self.subparsers[self.resource].description = description

        # parse any action arguments FIRST before attempting to parse
        if self.resource != 'settings':
            for method in ('list', 'modify', 'create'):
                if method in parser.parser.choices:
                    if method == 'list':
                        http_method = 'GET'
                    elif method == 'modify' and 'PUT' in parser.options:
                        http_method = 'PUT'
                    else:
                        http_method = 'POST'
                    parser.build_query_arguments(method, http_method)

        # Resource-level help, e.g. `ascender users --help`, where a resource is
        # named but no action is. We handle it by hand because add_help is off
        # for the resource subparsers, and only here, once every action has been
        # registered above, so that the help lists them rather than nothing.
        if self.help and not from_sphinx:
            non_option_args = self._get_non_option_args()
            if len(non_option_args) == 1 and non_option_args[0] == self.resource:
                self.subparsers[self.resource].print_help()
                raise SystemExit()

        if from_sphinx:
            # Our Sphinx plugin runs `parse_action` for *every* available
            # resource + action in the API so that it can generate usage
            # strings for automatic doc generation.
            #
            # Because of this behavior, we want to silently ignore the
            # `SystemExit` argparse will raise when you're missing required
            # positional arguments (which some actions have).
            try:
                self.parser.parse_known_args(self.argv)[0]
            except SystemExit:
                pass
            parsed, extra = self.parser.parse_known_args(self.argv)
        else:
            # Try to parse to determine if help is requested for a specific action
            try:
                self.parser.parse_known_args()[0]
            except SystemExit:
                # This happens when required arguments are missing, which is expected behavior
                # Let argparse handle it and show the appropriate help
                raise
            parsed, extra = self.parser.parse_known_args()

        if extra and self.verbose:
            # If extraneous arguments were provided, warn the user
            cprint('{}: unrecognized arguments: {}'.format(self.parser.prog, ' '.join(extra)), 'yellow', file=self.stdout)

        # build a dictionary of all of the _valid_ flags specified on the
        # command line so we can pass them on to the underlying ascenderkit call
        # we ignore special global flags like `--help` and `--conf.xyz`, and
        # the positional resource argument (i.e., "jobs")
        # everything else is a flag used as a query argument for the HTTP
        # request we'll make (e.g., --username="Joe", --verbosity=3)
        parsed = parsed.__dict__
        parsed = dict((k, v) for k, v in parsed.items() if (v is not None and k not in ('help', 'resource') and not k.startswith('conf.')))

        # if `id` is one of the arguments, it's a detail view
        if 'id' in parsed:
            page.endpoint += '{}/'.format(str(parsed.pop('id')))

        # determine the ascenderkit method to call
        action = self.original_action = parsed.pop('action')
        page, action = handle_custom_actions(self.resource, action, page)
        self.method = {
            'list': 'get',
            'modify': 'patch',
        }.get(action, action)

        if self.method == 'patch' and not parsed:
            # If we're doing an HTTP PATCH with an empty payload,
            # just print the help message (it's a no-op anyways)
            parser.parser.choices['modify'].print_help()
            return

        if self.help:
            # If --help is specified on a subarg parser, bail out
            # and print its help text
            parser.parser.choices[self.original_action].print_help()
            return

        if self.original_action == 'create':
            return page.post(parsed)

        return getattr(page, self.method)(**parsed)

    def parse_args(self, argv, env=None):
        """Configure the global parser.ArgumentParser object and apply
        global flags (such as --help, authentication, and formatting arguments)
        """
        env = env or os.environ
        self.argv = argv
        self.parser = HelpfulArgumentParser(add_help=False)
        self.parser.add_argument(
            '-h',
            '--help',
            action='store_true',
            help='prints usage information for the ascender tool',
        )
        self.parser.add_argument('--version', dest='conf.version', action='version', help='display ascender CLI version', version=__version__)
        add_authentication_arguments(self.parser, env)
        add_output_formatting_arguments(self.parser, env)

        self.args = self.parser.parse_known_args(self.argv)[0]
        self.verbose = self.get_config('verbose')
        if self.verbose:
            logging.basicConfig(level='DEBUG')
        self.color = self.get_config('color')
        if not self.color:
            disable_color()
        fmt = self.get_config('format')
        if fmt not in FORMATTERS.keys():
            self.parser.error('No formatter %s available.' % (fmt))
