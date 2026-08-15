import types
import os

from .utils import (
    PseudoNamespace,
    load_credentials,
    load_projects,
    to_bool,
)

config = PseudoNamespace()


def getvalue(self, name):
    return self.__getitem__(name)


if os.getenv('ASCENDERKIT_BASE_URL'):
    config.base_url = os.getenv('ASCENDERKIT_BASE_URL')

if os.getenv('ASCENDERKIT_CREDENTIAL_FILE'):
    config.credentials = load_credentials(os.getenv('ASCENDERKIT_CREDENTIAL_FILE'))

if os.getenv('ASCENDERKIT_PROJECT_FILE'):
    # Read the path from the environment, as the line above does. Reading it
    # from `config` instead handed load_projects a None it treats as "no file",
    # so the one named here was never opened.
    config.project_urls = load_projects(os.getenv('ASCENDERKIT_PROJECT_FILE'))

# kludge to mimic pytest.config
config.getvalue = types.MethodType(getvalue, config)

config.assume_untrusted = config.get('assume_untrusted', True)

config.client_connection_attempts = int(os.getenv('ASCENDERKIT_CLIENT_CONNECTION_ATTEMPTS', 5))
config.prevent_teardown = to_bool(os.getenv('ASCENDERKIT_PREVENT_TEARDOWN', False))
config.use_sessions = to_bool(os.getenv('ASCENDERKIT_SESSIONS', False))
config.api_base_path = os.getenv('ASCENDERKIT_API_BASE_PATH', '/api/')
