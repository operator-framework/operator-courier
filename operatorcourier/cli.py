import argparse
import pkg_resources
import sys
from operatorcourier import api


def main():
    """Generate the CLI bits
    """
    try:
        parser = _CliParser()
        parser.parse()
    except Exception as e:  # Exception raised to CLI should not be thrown to users,
        sys.exit(str(e))    # it should just be captured by logs


class _CliParser():
    """Class that generates the command line bits for the operator-courier cli tool
    """

    def __init__(self):
        pass

    def parse(self):
        """Parse generates and evaluates the command level parser
        """
        parser = argparse.ArgumentParser(
            description='Build, verify and push operator bundles into '
                        'external app registry',
            usage='''operator-courier <command> [<args>]

These are the commands you can use:
    verify      Create a bundle and test it for correctness.
    push        Create a bundle, test it, and push it to an app registry.
    nest        Take a flat to-be-bundled directory and version nest it.
''')
        try:
            __version__ = pkg_resources.get_distribution('operator-courier').version
        except Exception:
            __version__ = 'unknown'

        parser.add_argument('command', help='Subcommand to run')
        parser.add_argument('-v', '--version', help='Show the current version of operator-courier',
                            action='version', version=__version__)

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            parser.error('Unrecognized command')

        getattr(self, args.command)()

    # Parse the verify command
    def verify(self):
        parser = argparse.ArgumentParser(
            description='Build and verify an operator bundle to test')
        parser.add_argument('source_dir', help='Path of your directory of yaml '
                            'files to bundle. Either set this or '
                            'use the files argument for bundle data.')
        parser.add_argument('--ui_validate_io',
                            help='Validate bundle for operatorhub.io UI',
                            action='store_true')
        parser.add_argument('--validation-output', dest='validation_output',
                            help='A file to write validation warnings and errors to'
                                 'in JSON format')
        args, leftovers = parser.parse_known_args(sys.argv[2:])
        api.build_and_verify(source_dir=args.source_dir,
                             ui_validate_io=args.ui_validate_io,
                             validation_output=args.validation_output)

    # Parse the push command
    def push(self):
        parser = argparse.ArgumentParser(
            description='Build, verify and push an operator bundle '
                        'into external app registry.')
        parser.add_argument('source_dir',
                            help='Path of your directory of yaml files to bundle.')
        parser.add_argument('namespace',
                            help='Name of the Quay namespace to push operator to.')
        parser.add_argument('repository',
                            help='Application repository name '
                                 'the application is bundled for.')
        parser.add_argument('release',
                            help='The release version of the bundle.')
        parser.add_argument('token', help='Authorization token for Quay api.')
        parser.add_argument('--validation-output', dest='validation_output',
                            help='A file to write validation warnings and errors to'
                                 'in JSON format')
        args, leftovers = parser.parse_known_args(sys.argv[2:])
        api.build_verify_and_push(args.namespace,
                                  args.repository,
                                  args.release,
                                  args.token,
                                  source_dir=args.source_dir,
                                  validation_output=args.validation_output)

    # Parse the nest command
    def nest(self):
        parser = argparse.ArgumentParser(
            description='Take a flat bundle directory and version nest it '
                        'to eventually create an operator-registry image.')
        parser.add_argument('source_dir',
                            help='Path of your directory of yaml files to bundle.')
        parser.add_argument('registry_dir',
                            help='Path of your directory to be populated. '
                                 'If directory does not exist, it will be created.')

        args, leftovers = parser.parse_known_args(sys.argv[2:])
        api.nest(args.source_dir, args.registry_dir)
