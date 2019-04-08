import argparse
import pkg_resources
import sys
import logging
import traceback

from operatorcourier import api


def main():
    """Generate the CLI bits
    """
    try:
        parser = _CliParser()
        parser.parse()
    except Exception as e:  # Exception raised to CLI should not be thrown to users,
        logger = logging.getLogger(__name__)
        logger.debug("Exit traceback: %s", traceback.format_exc())
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
                        'external app registry')

        try:
            __version__ = pkg_resources.get_distribution('operator-courier').version
        except Exception:
            __version__ = 'unknown'

        parser.add_argument(
            '-v', '--version',
            help='Show the current version of operator-courier',
            action='version', version=__version__)
        parser.add_argument(
            '--verbose', dest='verbose',
            help="Provide detailed logs",
            action='store_true', default=False)

        subparsers = parser.add_subparsers(title='subcommands')

        verify_parser = subparsers.add_parser(
            'verify',
            help='Create a bundle and test it for correctness.',
            description='Build and verify an operator bundle to test')
        verify_parser.add_argument(
            'source_dir',
            help='Path of your directory of yaml files to bundle. '
            'Either set this or use the files argument for bundle data.')
        verify_parser.add_argument(
            '--ui_validate_io',
            help='Validate bundle for operatorhub.io UI. '
            'To visually confirm that your operator will be displayed correctly, '
            'please visit https://operatorhub.io/preview and paste '
            'your operator CSV.',
            action='store_true')
        verify_parser.add_argument(
            '--validation-output',
            dest='validation_output',
            help='A file to write validation warnings and errors to in JSON format')
        verify_parser.set_defaults(func=self.verify)

        push_parser = subparsers.add_parser(
            'push',
            help='Create a bundle, test it, and push it to an app registry.',
            description='Build, verify and push an operator bundle '
            'into external app registry.')
        push_parser.add_argument(
            'source_dir',
            help='Path of your directory of yaml files to bundle.')
        push_parser.add_argument(
            'namespace',
            help='Name of the Quay namespace to push operator to.')
        push_parser.add_argument(
            'repository',
            help='Application repository name the application is bundled for.')
        push_parser.add_argument(
            'release',
            help='The release version of the bundle.')
        push_parser.add_argument(
            'token',
            help='Authorization token for Quay api.')
        push_parser.add_argument(
            '--validation-output',
            dest='validation_output',
            help='A file to write validation warnings and errors to in JSON format')
        push_parser.set_defaults(func=self.push)

        nest_parser = subparsers.add_parser(
            'nest',
            help='Take a flat to-be-bundled directory and version nest it.',
            description='Take a flat bundle directory and version nest it '
            'to eventually create an operator-registry image.')
        nest_parser.add_argument(
            'source_dir',
            help='Path of your directory of yaml files to bundle.')
        nest_parser.add_argument(
            'registry_dir',
            help='Path of your directory to be populated. '
            'If directory does not exist, it will be created.')
        nest_parser.set_defaults(func=self.nest)

        flatten_parser = subparsers.add_parser(
            'flatten',
            help='Create a flat directory from versioned operator bundle yaml files.',
            description='Given a directory with different versions of '
            'operator bundles (CRD, CSV, package), this command extracts '
            'versioned CSVs and the latest version of each CRD along with '
            'the package file and creates a new flat directory '
            'of yaml files. See https://github.com/operator-framework/'
            'operator-registry#manifest-format to find out more about '
            'how nested bundles should be structured.')
        flatten_parser.add_argument(
            'source_dir',
            help='Path of the source directory that contains different '
            'versions of operator bundles (CRD, CSV, package)')
        flatten_parser.add_argument(
            'dest_dir',
            help='The new flat directory that contains '
            'extracted bundle files')
        flatten_parser.set_defaults(func=self.flatten)

        args = parser.parse_args()
        logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.WARNING
        )

        func = getattr(args, 'func', None)
        if callable(func):
            func(args)
        else:
            parser.print_help(sys.stderr)
            sys.exit(2)

    def verify(self, args):
        """Run the verify command
        """
        api.build_and_verify(source_dir=args.source_dir,
                             ui_validate_io=args.ui_validate_io,
                             validation_output=args.validation_output)

    def push(self, args):
        """Run the push command
        """
        api.build_verify_and_push(args.namespace,
                                  args.repository,
                                  args.release,
                                  args.token,
                                  source_dir=args.source_dir,
                                  validation_output=args.validation_output)

    def nest(self, args):
        """Run the nest command
        """
        api.nest(args.source_dir, args.registry_dir)

    def flatten(self, args):
        """Parse the flatten command
        """
        api.flatten(args.source_dir, args.dest_dir)
