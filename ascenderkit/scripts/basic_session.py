from argparse import ArgumentParser
import logging
import pdb  # noqa
import sys
import os

from ascenderkit import api, config, utils, exceptions, WSClient  # noqa
from ascenderkit.ascender.utils import check_related, delete_all, get_all, uses_sessions  # noqa
from ascenderkit.ascender.utils import as_user as _as_user

if str(os.getenv('ASCENDERKIT_DEBUG', 'false')).lower() in ['true', '1']:
    logging.basicConfig(level='DEBUG')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--base-url',
        dest='base_url',
        default=os.getenv('ASCENDERKIT_BASE_URL', 'http://127.0.0.1:8013'),
        help='URL for Ascender.  Defaults to env var ASCENDERKIT_BASE_URL or http://127.0.0.1:8013',
    )
    parser.add_argument(
        '-c',
        '--credential-file',
        dest='credential_file',
        default=os.getenv('ASCENDERKIT_CREDENTIAL_FILE', utils.not_provided),
        help='Path for yml credential file.  If not provided or set by ASCENDERKIT_CREDENTIAL_FILE, set '
        'ASCENDERKIT_USER and ASCENDERKIT_USER_PASSWORD env vars for ascender user credentials.',
    )
    parser.add_argument(
        '-p',
        '--project-file',
        dest='project_file',
        default=os.getenv('ASCENDERKIT_PROJECT_FILE'),
        help='Path for yml project config file.If not provided or set by ASCENDERKIT_PROJECT_FILE, projects will not have default SCM_URL',
    )
    parser.add_argument('-f', '--file', dest='session_script', default=False, help='script file to run in the interactive session.')
    parser.add_argument('-x', '--non-interactive', action='store_true', dest='non_interactive', help='Do not run in interactive mode.')
    return parser.parse_known_args()[0]


def main():
    exc = None
    try:
        global session_args
        session_args = parse_args()
        config.base_url = session_args.base_url

        if session_args.credential_file != utils.not_provided:
            config.credentials = utils.load_credentials(session_args.credential_file)
        else:
            config.credentials = utils.PseudoNamespace(
                {'default': {'username': os.getenv('ASCENDERKIT_USER', 'admin'), 'password': os.getenv('ASCENDERKIT_USER_PASSWORD', 'password')}}
            )

        if session_args.project_file != utils.not_provided:
            config.project_urls = utils.load_projects(session_args.project_file)

        global root
        root = api.Api()
        if uses_sessions(root.connection):
            config.use_sessions = True
            root.load_session().get()
        else:
            root.load_authtoken().get()

        if 'v2' in root.available_versions:
            global v2
            v2 = root.available_versions.v2.get()

        rc = 0
        if session_args.session_script:
            try:
                with open(session_args.session_script) as script:
                    exec(script.read(), globals())
            except Exception as e:
                exc = e
                raise
    except Exception as e:
        exc = e  # noqa
        rc = 1  # noqa
        raise


def as_user(username, password=None):
    return _as_user(root, username, password)


def load_interactive():
    if '--help' in sys.argv or '-h' in sys.argv:
        return parse_args()

    if '-x' in sys.argv or '--non-interactive' in sys.argv:
        # Set the session up, run the --file script if one was given, and
        # return, rather than dropping into a prompt nobody asked for.
        return main()

    try:
        from IPython import start_ipython

        basic_session_path = os.path.abspath(__file__)
        if basic_session_path[-1] == 'c':  # start_ipython doesn't work w/ .pyc
            basic_session_path = basic_session_path[:-1]
        sargs = ['-i', basic_session_path]
        if sys.argv[1:]:
            sargs.extend(['--'] + sys.argv[1:])
        return start_ipython(argv=sargs)
    except ImportError:
        from code import interact

        main()
        interact('', local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()
