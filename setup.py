import os
import glob
import shutil
from setuptools import setup, find_packages, Command


def use_scm_version():
    return False if version_file() else True


def get_version_from_file():
    vf = version_file()
    if vf:
        with open(vf, 'r') as file:
            return file.read().strip()


def version_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(current_dir, 'VERSION')

    if os.path.exists(version_file):
        return version_file


def setup_requires():
    if version_file():
        return []
    else:
        return ['setuptools_scm']


def long_description():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'README.md'), 'r') as readme:
        return readme.read()


extra_setup_args = {}
if not version_file():
    # The package sits at the root of its own repository, so setuptools_scm
    # reads the tags from here rather than from a parent checkout.
    extra_setup_args.update(dict(use_scm_version=dict(root=".", relative_to=__file__), setup_requires=setup_requires()))


class CleanCommand(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

        # List of things to remove
        rm_list = list()

        # Find any .pyc files or __pycache__ dirs
        for root, dirs, files in os.walk(self.cwd, topdown=False):
            for fname in files:
                if fname.endswith('.pyc') and os.path.isfile(os.path.join(root, fname)):
                    rm_list.append(os.path.join(root, fname))
            if root.endswith('__pycache__'):
                rm_list.append(root)

        # Find egg's
        for egg_dir in glob.glob('*.egg') + glob.glob('*egg-info'):
            rm_list.append(egg_dir)

        # Zap!
        for rm in rm_list:
            if self.verbose:
                print("Removing '%s'" % rm)
            if os.path.isdir(rm):
                if not self.dry_run:
                    shutil.rmtree(rm)
            else:
                if not self.dry_run:
                    os.remove(rm)


setup(
    name='ascender-kit',
    version=get_version_from_file(),
    description='The official command line interface for Ascender Automation',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    author='Ascender Project Contributors',
    author_email='info@ctrliq.com',
    url='https://github.com/ctrliq/ascender-kit',
    project_urls={
        'Homepage': 'https://ascender-automation.org',
        'Source': 'https://github.com/ctrliq/ascender-kit',
        'Issues': 'https://github.com/ctrliq/ascender-kit/issues',
    },
    packages=find_packages(exclude=['test', 'test.*']),
    cmdclass={
        'clean': CleanCommand,
    },
    include_package_data=True,
    install_requires=[
        # packaging backs ascenderkit.ascender.version_cmp, which __init__
        # imports unconditionally, so it is needed for `import ascenderkit`.
        'packaging',
        'PyYAML',
        'requests',
        # Imported directly by the CLI to silence insecure-request warnings.
        # It arrives with requests today, but relying on that is fragile.
        'urllib3',
    ],
    python_requires=">=3.11",
    extras_require={'formatting': ['jq'], 'websockets': ['websocket-client>=1.0.0'], 'crypto': ['cryptography']},
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
    ],
    entry_points={'console_scripts': ['ascender-shell=ascenderkit.scripts.basic_session:load_interactive', 'ascender=ascenderkit.cli:run']},
    **extra_setup_args,
)
