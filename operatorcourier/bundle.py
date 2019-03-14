import copy
import itertools
import json
import logging
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory

from operatorcourier.build import BuildCmd
from operatorcourier.validate import ValidateCmd
from operatorcourier.push import PushCmd
from operatorcourier.format import format_bundle
from operatorcourier.errors import OpCourierBadBundle

logger = logging.getLogger(__name__)


class OperatorBundle:
    """Represents operator bundles, provides validation and push methods.

    Build a new bundle using one of the following methods:
        OperatorBundle.from_yaml_data()
        OperatorBundle.from_directory()

    The build methods accept validation parameters and will run validation
    immediately after building. If you need to re-run validation with different
    parameters, you can use the validate() method.
    """

    def __init__(self):
        self._data = {}
        self._valid = False
        self._validation_info = None

    def data_copy(self):
        """Copy the bundle data (the original data must not be modified).

        :return: A copy of the data in this bundle.
        """
        return copy.deepcopy(self._data)

    @property
    def valid(self):
        return self._valid

    @property
    def validation_info(self):
        return self._validation_info

    @classmethod
    def from_yaml_data(cls, yaml_data, **validation_args):
        """Build an operator bundle from a list of yaml strings and validate it.

        :param yaml_data: List of yaml strings to build this bundle from.
        :param validation_args: Arguments for validation. See the validate()
                                method for an accurate signature.

        :raises OpCourierBadYaml: When an invalid yaml file is encountered.
        :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}.

        :return: A validated operator bundle.
        """
        bundle = cls()
        data = BuildCmd().build_bundle(yaml_data)
        bundle._data = data

        bundle.validate(**validation_args)
        return bundle

    @classmethod
    def from_directory(cls, directory, **validation_args):
        """Build an operator bundle from all y(a?)ml files in a directory
        (top level only, no recursion) and validate it.

        :param directory: Path to directory with yaml files for this bundle.
        :param validation_args: Arguments for validation. See the validate()
                                method for an accurate signature.

        :raises OpCourierBadYaml: When an invalid yaml file is encountered.
        :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}.

        :return: A validated operator bundle.
        """
        d = Path(directory)
        yaml_files = itertools.chain(d.glob('*.yml'), d.glob('*.yaml'))
        yaml_strings = (f.read_text() for f in yaml_files)

        return cls.from_yaml_data(yaml_strings, **validation_args)

    def validate(self, repository=None, ui_validate_io=False):
        """Validate the bundle and save the info collected during validation.

        :param repository: Optionally, check that the package name in the bundle
                           matches the specified repository name.
        :param ui_validate_io: Run additional operatorhub.io UI validation?
        """
        valid, info = ValidateCmd(ui_validate_io).validate(self._data, repository)
        self._valid = valid
        self._validation_info = info

    def push(self, namespace, repository, release, auth_token):
        """Format the bundle and push it to Quay.io.

        :param namespace: Namespace that contains the repository for the application.
        :param repository: Repository name of the application described by the bundle.
        :param release: Release version of the bundle.
        :param auth_token: Authentication token used to push to Quay.io.

        :raises OpCourierBadBundle: When attempting to push an invalid bundle.
        :raises OpCourierQuayError: When an error occurs while pushing to Quay.
        """
        if not self.valid:
            logger.error("Bundle failed validation.")
            raise OpCourierBadBundle(
                'Resulting bundle is invalid, input yaml is improperly defined.',
                validation_info=self.validation_info
            )

        with TemporaryDirectory() as tmp_dir:
            bundle = format_bundle(self._data)
            bundle_path = Path(tmp_dir) / 'bundle.yaml'

            with bundle_path.open('w') as outfile:
                yaml.dump(bundle, outfile, default_flow_style=False)
                outfile.flush()

            PushCmd().push(tmp_dir, namespace, repository, release, auth_token)

    def write_validation_info(self, out_file):
        """Write the info collected during validation to a file (as json).

        :param out_file: The file which the validation info will be written to.
        """
        with open(out_file, 'w') as f:
            json.dump(self.validation_info, f)
            f.write('\n')
