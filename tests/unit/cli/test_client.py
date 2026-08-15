import sys
from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError

from ascenderkit.cli import run, CLI


class MockedCLI(CLI):
    def fetch_version_root(self):
        pass

    @property
    def v2(self):
        return MockedCLI()

    @property
    def json(self):
        return {'users': None}


@pytest.mark.parametrize('help_param', ['-h', '--help'])
def test_help(capfd, help_param):
    with pytest.raises(SystemExit):
        run(['ascender {}'.format(help_param)])
    out, err = capfd.readouterr()

    assert "usage:" in out
    for snippet in ('--conf.host https://example.ascender.org]', '-v, --verbose'):
        assert snippet in out


def test_connection_error(capfd):
    cli = CLI()
    cli.parse_args(['ascender'])
    with pytest.raises(ConnectionError):
        cli.connect()


@pytest.mark.parametrize('resource', ['', 'invalid'])
def test_list_resources(capfd, resource):
    # if a valid resource isn't specified, print --help
    cli = MockedCLI()
    cli.parse_args(['ascender {}'.format(resource)])
    cli.connect()

    try:
        cli.parse_resource()
        out, err = capfd.readouterr()
    except SystemExit:
        # python2 argparse raises SystemExit for invalid/missing required args,
        # py3 doesn't
        _, out = capfd.readouterr()

    assert "usage:" in out
    for snippet in ('--conf.host https://example.ascender.org]', '-v, --verbose'):
        assert snippet in out


class TestHelpHandling:
    """Test suite for improved help handling functionality"""

    def test_get_non_option_args_basic(self):
        """Test _get_non_option_args extracts non-option arguments correctly"""
        cli = CLI()
        cli.argv = ['ascender', 'users', 'list', '--verbose']

        result = cli._get_non_option_args()
        assert result == ['users', 'list']

    def test_get_non_option_args_with_flags(self):
        """Test _get_non_option_args ignores option flags and their values"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host', 'example.com', 'jobs', 'create', '--name', 'test']

        result = cli._get_non_option_args()
        # Should only include positional arguments, not option values
        assert result == ['jobs', 'create']

    def test_get_non_option_args_before_help(self):
        """Test _get_non_option_args with before_help=True stops at help flag"""
        cli = CLI()
        cli.argv = ['ascender', 'users', '--help', 'extra', 'args']

        result = cli._get_non_option_args(before_help=True)
        assert result == ['users']

    def test_get_non_option_args_before_help_short_flag(self):
        """Test _get_non_option_args with before_help=True stops at -h flag"""
        cli = CLI()
        cli.argv = ['ascender', 'projects', '-h', 'should', 'not', 'appear']

        result = cli._get_non_option_args(before_help=True)
        assert result == ['projects']

    def test_get_non_option_args_no_help_flag(self):
        """Test _get_non_option_args when help flag not present"""
        cli = CLI()
        cli.argv = ['ascender', 'organizations', 'list']

        result = cli._get_non_option_args(before_help=True)
        assert result == ['organizations', 'list']

    def test_is_main_help_request_true(self):
        """Test _is_main_help_request returns True for main CLI help"""
        cli = CLI()
        cli.argv = ['ascender', '--help']

        result = cli._is_main_help_request()
        assert result is True

    def test_is_main_help_request_short_flag(self):
        """Test _is_main_help_request returns True for main CLI help with -h"""
        cli = CLI()
        cli.argv = ['ascender', '-h']

        result = cli._is_main_help_request()
        assert result is True

    def test_is_main_help_request_false_subcommand(self):
        """Test _is_main_help_request returns False for subcommand help"""
        cli = CLI()
        cli.argv = ['ascender', 'users', '--help']

        result = cli._is_main_help_request()
        assert result is False

    def test_is_main_help_request_false_action(self):
        """Test _is_main_help_request returns False for action help"""
        cli = CLI()
        cli.argv = ['ascender', 'jobs', 'create', '--help']

        result = cli._is_main_help_request()
        assert result is False

    def test_is_main_help_request_false_no_help(self):
        """Test _is_main_help_request returns False when no help flag"""
        cli = CLI()
        cli.argv = ['ascender', 'users', 'list']

        result = cli._is_main_help_request()
        assert result is False

    def test_main_help_does_not_exit_during_arg_parsing(self):
        """Main help must survive parse_args so the resource list can be built.

        Upstream exits here to avoid contacting the server, but the resource
        list is discovered from the server and is the substance of the help
        output, so exiting early empties it. It also aborts the Sphinx build,
        which constructs this parser only in order to document it.
        """
        cli = CLI()
        cli.argv = ['ascender', '--help']
        assert cli._is_main_help_request() is True

        with patch.object(sys, 'exit') as mock_exit:
            cli.parse_args(['ascender', '--help'])
            mock_exit.assert_not_called()
        assert cli.parser is not None

    def test_no_early_exit_for_subcommand_help(self):
        """Test that subcommand help does not exit early"""
        with patch.object(sys, 'exit') as mock_exit:
            cli = CLI()
            # This should not exit early since it's subcommand help
            cli.parse_args(['ascender', 'users', '--help'])

            mock_exit.assert_not_called()

    def test_help_property_detection(self):
        """Test that help property correctly detects help flags"""
        cli = CLI()

        cli.argv = ['ascender', '--help']
        assert cli.help is True

        cli.argv = ['ascender', '-h']
        assert cli.help is True

        cli.argv = ['ascender', 'users', '--help']
        assert cli.help is True

        cli.argv = ['ascender', 'users', 'list']
        assert cli.help is False

    def test_short_help_flag_added(self):
        """Test that -h flag is properly added to argument parser"""
        cli = CLI()
        cli.parse_args(['ascender'])

        # Verify that both -h and --help are recognized
        help_actions = [action for action in cli.parser._actions if '--help' in action.option_strings]
        assert len(help_actions) == 1
        assert '-h' in help_actions[0].option_strings
        assert '--help' in help_actions[0].option_strings

    def test_get_non_option_args_with_equals_format(self):
        """Test _get_non_option_args handles --opt=val format correctly"""
        cli = CLI()
        cli.argv = ['ascender', 'users', 'create', '--email=john@example.com', '--name=john']

        result = cli._get_non_option_args()
        assert result == ['users', 'create']

    def test_get_non_option_args_mixed_option_formats(self):
        """Test _get_non_option_args handles mixed --opt=val and --opt val formats"""
        cli = CLI()
        cli.argv = ['ascender', 'jobs', 'launch', '--job-template=5', '--extra-vars', '{"key": "value"}', 'extra_arg']

        result = cli._get_non_option_args()
        assert result == ['jobs', 'launch', 'extra_arg']

    def test_get_non_option_args_short_options(self):
        """Test _get_non_option_args handles short options correctly"""
        cli = CLI()
        cli.argv = ['ascender', '-v', '-f', 'json', 'projects', 'list']

        result = cli._get_non_option_args()
        assert result == ['projects', 'list']

    def test_get_non_option_args_consecutive_options(self):
        """Test _get_non_option_args with consecutive options"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host', 'example.com', '--conf.username', 'admin', 'teams', 'create']

        result = cli._get_non_option_args()
        assert result == ['teams', 'create']

    def test_get_non_option_args_option_at_end(self):
        """Test _get_non_option_args with option at the end"""
        cli = CLI()
        cli.argv = ['ascender', 'users', 'list', '--format', 'table']

        result = cli._get_non_option_args()
        assert result == ['users', 'list']

    def test_get_non_option_args_flag_only_options(self):
        """Test _get_non_option_args with flag-only options (no values)"""
        cli = CLI()
        # More realistic: flags at the end or grouped together
        cli.argv = ['ascender', 'organizations', 'list', '--verbose', '--insecure', '--monitor']

        result = cli._get_non_option_args()
        assert result == ['organizations', 'list']

    def test_get_non_option_args_option_value_looks_like_option(self):
        """Test _get_non_option_args when option value starts with dash"""
        cli = CLI()
        cli.argv = ['ascender', 'jobs', 'create', '--description', '-some-description-with-dashes', 'template']

        result = cli._get_non_option_args()
        # Values starting with '-' are treated as options, and 'template' becomes the value for that "option"
        # Users should use --description="-some-value" format for values starting with dash
        assert result == ['jobs', 'create']

    def test_get_non_option_args_complex_scenario(self):
        """Test _get_non_option_args with complex mixed arguments"""
        cli = CLI()
        cli.argv = [
            'ascender',
            '--conf.host=https://example.com',
            'job_templates',
            'create',
            '--name',
            'my-template',
            '--job-type=run',
            '--inventory',
            '1',
            '--project=2',
            '--verbose',
        ]

        result = cli._get_non_option_args()
        assert result == ['job_templates', 'create']

    def test_get_non_option_args_before_help_with_options(self):
        """Test _get_non_option_args before_help=True with options before help"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host', 'example.com', 'users', 'create', '--name=test', '--help', 'ignored']

        result = cli._get_non_option_args(before_help=True)
        assert result == ['users', 'create']

    def test_get_non_option_args_before_help_only_options(self):
        """Test _get_non_option_args before_help=True with only options before help"""
        cli = CLI()
        cli.argv = ['ascender', '--verbose', '--conf.host=example.com', '--help', 'users', 'list']

        result = cli._get_non_option_args(before_help=True)
        assert result == []

    def test_is_main_help_request_with_options_before_help(self):
        """Test _is_main_help_request with options but no subcommands before help"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host=example.com', '--verbose', '--help']

        result = cli._is_main_help_request()
        assert result is True

    def test_is_main_help_request_false_with_subcommand_and_options(self):
        """Test _is_main_help_request returns False when subcommand present with options"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host', 'example.com', 'users', '--format=json', '--help']

        result = cli._is_main_help_request()
        assert result is False

    def test_is_main_help_request_false_option_value_looks_like_subcommand(self):
        """Test _is_main_help_request doesn't mistake option values for subcommands"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.host', 'users', '--help']  # 'users' is option value, not subcommand

        result = cli._is_main_help_request()
        assert result is True  # Should be True since 'users' is just an option value

    def test_is_main_help_request_complex_option_scenario(self):
        """Test _is_main_help_request with complex option scenario"""
        cli = CLI()
        cli.argv = ['ascender', '--conf.username=admin', '--conf.password', 'secret', 'job_templates', '--help']

        result = cli._is_main_help_request()
        assert result is False  # 'job_templates' is a real subcommand, not an option value

    def test_empty_args_handling(self):
        """Test _get_non_option_args handles minimal arguments"""
        cli = CLI()
        cli.argv = ['ascender']

        result = cli._get_non_option_args()
        assert result == []

    def test_only_program_name_and_options(self):
        """Test _get_non_option_args with only the program name and options"""
        cli = CLI()
        cli.argv = ['ascender', '--verbose', '--conf.host=example.com']

        result = cli._get_non_option_args()
        assert result == []

    def test_get_non_option_args_dash_value_with_equals(self):
        """Test _get_non_option_args handles dash values correctly with equals format"""
        cli = CLI()
        cli.argv = ['ascender', 'jobs', 'create', '--description=-some-description-with-dashes', 'template']

        result = cli._get_non_option_args()
        # Using --opt=val format correctly handles values starting with dash
        assert result == ['jobs', 'create', 'template']


class TestSphinxParserBuild:
    """The sphinx plugin builds this parser purely in order to document it."""

    def test_building_the_parser_never_exits(self):
        # An exit here aborts the Sphinx build mid-run, and because the status
        # is 0 the build looks successful while producing no pages at all.
        cli = CLI()
        cli.parse_args(['ascender', '--help'])
        assert cli.parser is not None

    def test_unreachable_server_still_yields_global_help(self):
        # A bare `ascender --help` against a server that is not there should
        # print the global help rather than raise.
        cli = CLI()
        cli.parse_args(['ascender', '--conf.host', 'https://127.0.0.1:1', '--help'])
        assert cli._is_main_help_request() is True
        cli.connect()


class TestFlagsDoNotSwallowResources:
    """Options that take no value must not consume the token after them.

    `ascender -k users --help` names a resource. Treating every option as
    value-taking made `-k` eat `users`, so the invocation looked like plain
    `ascender --help`: resource-level help never fired, and the request was
    misread as a request for the global help.
    """

    @pytest.mark.parametrize(
        'argv, expected',
        [
            (['ascender', 'users', '--help'], ['users']),
            (['ascender', '-k', 'users', '--help'], ['users']),
            (['ascender', '--conf.insecure', 'users', '--help'], ['users']),
            (['ascender', '-v', 'users', 'list'], ['users', 'list']),
            (['ascender', '-k', '-v', 'jobs', 'list'], ['jobs', 'list']),
            # options that really do take a value still consume it
            (['ascender', '--conf.host', 'https://example.org', 'users', '--help'], ['users']),
            (['ascender', '-f', 'json', 'projects', 'list'], ['projects', 'list']),
            (['ascender', '--conf.username', 'admin', '-k', 'teams', 'get'], ['teams', 'get']),
        ],
    )
    def test_resource_survives_preceding_flags(self, argv, expected):
        cli = CLI()
        cli.parse_args(argv)
        assert cli._get_non_option_args() == expected

    @pytest.mark.parametrize(
        'argv',
        [
            ['ascender', '-k', 'users', '--help'],
            ['ascender', '-v', '-k', 'users', '--help'],
        ],
    )
    def test_flags_before_a_resource_are_not_main_help(self, argv):
        cli = CLI()
        cli.parse_args(argv)
        assert cli._is_main_help_request() is False

    @pytest.mark.parametrize('argv', [['ascender', '--help'], ['ascender', '-k', '--help'], ['ascender', '-k', '-v', '-h']])
    def test_flags_alone_are_still_main_help(self, argv):
        cli = CLI()
        cli.parse_args(argv)
        assert cli._is_main_help_request() is True

    def test_value_taking_options_are_identified_from_the_parser(self):
        cli = CLI()
        cli.parse_args(['ascender'])
        assert cli._option_takes_a_value('-k') is False
        assert cli._option_takes_a_value('-v') is False
        assert cli._option_takes_a_value('--help') is False
        assert cli._option_takes_a_value('--conf.host') is True
        assert cli._option_takes_a_value('-f') is True
        # Unknown options, and calls made before the parser exists, keep the
        # old assumption that a value follows.
        assert cli._option_takes_a_value('--not-an-option') is True
        assert CLI()._option_takes_a_value('-k') is True
