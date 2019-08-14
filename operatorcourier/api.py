"""
operatorcourier.api module

This module implements the api that should be imported
when using the operator-courier package
"""

import os
import logging
from tempfile import TemporaryDirectory
from distutils.dir_util import copy_tree
import yaml
from operatorcourier.verified_manifest import VerifiedManifest
from operatorcourier.push import PushCmd
from operatorcourier.nest import nest_bundles
from operatorcourier.flatten import flatten_bundles
from operatorcourier.errors import OpCourierBadBundle

logger = logging.getLogger(__name__)


def build_and_verify(source_dir=None, yamls=None, ui_validate_io=False,
                     validation_output=None, repository=None):
    """Build and verify constructs an operator bundle from
    a set of files and then verifies it for usefulness and accuracy.

    This API verifies the input source_dir or yamls and returns a verification
    object which contains a nested boolean that indicates if the source_dir
    is nested or not, and a bundle dictionary if the source_dir is in the flat structure.

    :param source_dir: Path to local directory of yaml files to be read.
    :param yamls: List of yaml strings to create bundle with
    :param ui_validate_io: Optional flag to test operatorhub.io specific validation
    :param validation_output: Path to optional output file for validation logs
    :param repository: Repository name for the application

    :raises TypeError: When called with both source_dir and yamls specified

    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    :raises OpCourierBadBundle: When the resulting bundle fails validation
    """

    if source_dir and yamls:
        msg = 'source_dir and yamls cannot both be specified.'
        logger.error(msg)
        raise TypeError(msg)

    verified_manifest = VerifiedManifest(source_dir, yamls, ui_validate_io, repository)

    if validation_output:
        verified_manifest.write_validation_to_file(validation_output)

    if not verified_manifest.is_valid:
        raise OpCourierBadBundle("Resulting bundle is invalid, "
                                 "input yaml is improperly defined.",
                                 verified_manifest.validation_dict)

    return verified_manifest


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
    :raises OpCourierBadBundle: When the resulting bundle fails validation

    :raises OpCourierQuayCommunicationError: When communication with Quay fails
    :raises OpCourierQuayErrorResponse: When Quay responds with an error
    :raises OpCourierQuayError: When the request fails in an unexpected way
    """
    verified_manifest = build_and_verify(source_dir, yamls, repository=repository,
                                         validation_output=validation_output)
    if not verified_manifest.nested:
        with TemporaryDirectory(prefix=repository+"-") as temp_dir:
            with open(os.path.join(temp_dir, 'bundle.yaml'), 'w') as outfile:
                yaml.dump(verified_manifest.bundle, outfile, default_flow_style=False)
            PushCmd().push(temp_dir, namespace, repository, revision, token)
    else:
        with TemporaryDirectory(prefix=repository+"-") as temp_dir:
            copy_tree(source_dir, temp_dir)
            PushCmd().push(temp_dir, namespace, repository, revision, token)


def nest(source_dir, output_dir):
    """Nest takes a flat bundle directory and version nests it
    to eventually be consumed as part of an operator-registry image build.

    This method will only extract valid operator manifest files and folders
    and ignore the rest.

    If the input directory is already nested, this method will copy the files and
    folders as is, with non-manifest files and folders excluded.


    :param source_dir: Path to local directory of yaml files to be read
    :param output_dir: Path of your directory to be populated.
                       If directory does not exist, it will be created.

    :raises OpCourierBadYaml: When an invalid yaml file is encountered
    """
    if source_dir and output_dir:
        nest_bundles(source_dir, output_dir)


def flatten(source_dir, dest_dir):
    """
    Given a directory containing different versions of operator bundles
    (CRD, CSV, package) in separate version directories, this function
    copies all files needed to the flattened directory. It is the inverse
    of the `nest` function.

    :param source_dir: the directory containing different versions
    of operator bundles (CRD, CSV, package) in separate version directories
    :param dest_dir: the flattened directory path where all necessary files are copied
    """
    os.makedirs(dest_dir, exist_ok=True)
    flatten_bundles(source_dir, dest_dir)
