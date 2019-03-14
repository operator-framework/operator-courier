"""
operatorcourier.api module

This module implements the api that should be imported
when using the operator-courier package
"""

import os
import logging
from tempfile import TemporaryDirectory

from operatorcourier.bundle import OperatorBundle
from operatorcourier.format import format_bundle
from operatorcourier.nest import nest_bundles
from operatorcourier.errors import OpCourierBadBundle

logger = logging.getLogger(__name__)


def build_and_verify(source_dir=None, yamls=None, ui_validate_io=False,
                     validation_output=None, repository=None):
    """Build and verify constructs an operator bundle from
    a set of files and then verifies it for usefulness and accuracy.

    It returns the bundle as a string.

    :param source_dir: Path to local directory of yaml files to be read.
    :param yamls: List of yaml strings to create bundle with
    :param ui_validate_io: Optional flag to test operatorhub.io specific validation
    :param validation_output: Path to optional output file for validation logs
    :param repository: Repository name for the application

    :raises TypeError: When called with both source_dir and yamls specified

    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}
    :raises OpCourierBadBundle: When the resulting bundle fails validation
    """
    bundle = build_bundle(source_dir, yamls,
                          repository=repository,
                          ui_validate_io=ui_validate_io)

    if validation_output is not None:
        bundle.write_validation_info(validation_output)

    if bundle.valid:
        bundle_data = format_bundle(bundle.data_copy())
        return bundle_data
    else:
        logger.error("Bundle failed validation.")
        raise OpCourierBadBundle(
            "Resulting bundle is invalid, input yaml is improperly defined.",
            validation_info=bundle.validation_info
        )


def build_verify_and_push(namespace, repository, revision, token,
                          source_dir=None, yamls=None,
                          validation_output=None):
    """Build verify and push constructs the operator bundle,
    verifies it, and pushes it to an external app registry.
    Currently the only supported app registry is the one
    located at Quay.io (https://quay.io/cnr/api/v1/packages/)

    :param namespace: Quay namespace where the repository we are
                      pushing the bundle is located.
    :param repository: Application repository name the application is bundled for.
    :param revision: Release version of the bundle.
    :param token: Basic authentication token used to authorize push to external datastore
    :param source_dir: Path to local directory of yaml files to be read
    :param yamls: List of yaml strings to create bundle with
    :param validation_output: Path to optional output file for validation logs

    :raises TypeError: When called with both source_dir and yamls specified

    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}
    :raises OpCourierBadBundle: When the resulting bundle fails validation

    :raises OpCourierQuayCommunicationError: When communication with Quay fails
    :raises OpCourierQuayErrorResponse: When Quay responds with an error
    """
    bundle = build_bundle(source_dir, yamls, repository=repository)

    if validation_output is not None:
        bundle.write_validation_info(validation_output)

    bundle.push(namespace, repository, revision, token)


def nest(source_dir, registry_dir):
    """Nest takes a flat bundle directory and version nests it
    to eventually be consumed as part of an operator-registry image build.

    :param source_dir: Path to local directory of yaml files to be read
    :param output_dir: Path of your directory to be populated.
                       If directory does not exist, it will be created.

    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}
    """

    yaml_files = []

    if source_dir is not None:
        for filename in os.listdir(source_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(source_dir + "/" + filename) as f:
                    yaml_files.append(f.read())

    with TemporaryDirectory() as temp_dir:
        nest_bundles(yaml_files, registry_dir, temp_dir)


def build_bundle(source_dir=None, yamls=None,
                 repository=None, ui_validate_io=False):
    """Build a bundle from a set of yaml files and validate it.

    Specifying both source_dir and yamls on function call is considered
    invalid usage and will raise a TypeError.

    Specifying neither results in an empty bundle.

    :param source_dir: Path to local directory of yaml files to be read.
    :param yamls: List of yaml strings to create bundle with
    :param repository: Optionally, check that the package name in the bundle
                       matches the specified repository name.
    :param ui_validate_io: Run additional operatorhub.io UI validation?

    :raises TypeError: When called with both source_dir and yamls specified
    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    :raises OpCourierBadArtifact: When a file is not any of {CSV, CRD, Package}

    :return: An OperatorBundle object containing the newly created bundle.
    """
    if source_dir is not None and yamls is not None:
        logger.error("Both source_dir and yamls cannot be defined.")
        raise TypeError(
            "Both source_dir and yamls cannot be specified on function call."
        )

    if source_dir is not None:
        bundle = OperatorBundle.from_directory(source_dir,
                                               repository=repository,
                                               ui_validate_io=ui_validate_io)
    else:
        bundle = OperatorBundle.from_yaml_data(yamls or [],
                                               repository=repository,
                                               ui_validate_io=ui_validate_io)

    return bundle
