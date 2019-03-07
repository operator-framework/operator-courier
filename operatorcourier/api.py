"""
operatorcourier.api module

This module implements the api that should be imported when using the operator-courier package
"""

import os
import logging
from tempfile import TemporaryDirectory
import yaml
from operatorcourier.build import BuildCmd
from operatorcourier.validate import ValidateCmd
from operatorcourier.push import PushCmd
from operatorcourier.format import format_bundle
from operatorcourier.nest import nest_bundles

logging.basicConfig()
logger = logging.getLogger(__name__)

def build_and_verify(source_dir=None, yamls=None, ui_validate_io=False):
    """Build and verify constructs an operator bundle from a set of files and then verifies it for usefulness and accuracy.
    It returns the bundle as a string.

    :param source_dir: Path to local directory of yaml files to be read.
    :param yamls: List of yaml strings to create bundle with
    """

    if source_dir is not None and yamls is not None:
        logger.error("Both source_dir and yamls cannot be defined.")
        raise TypeError("Both source_dir and yamls cannot be specified on function call.")

    yaml_files = []

    if source_dir is not None: 
        for filename in os.listdir(source_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(source_dir + "/" + filename) as f:
                    yaml_files.append(f.read())
    elif yamls is not None:
        yaml_files = yamls

    bundle = BuildCmd().build_bundle(yaml_files)

    valid = ValidateCmd(ui_validate_io).validate(bundle)

    if not valid:
        bundle = None
        logger.error("Bundle failed validation.")
    else:
        bundle = format_bundle(bundle)
    
    return bundle

def build_verify_and_push(namespace, repository, revision, token, source_dir=None, yamls=None):
    """Build verify and push constructs the operator bundle, verifies it, and pushes it to an external app registry.
    Currently the only supported app registry is the one located at Quay.io (https://quay.io/cnr/api/v1/packages/)

    :param namespace: Quay namespace where the repository we are pushing the bundle is located.
    :param repository: Application repository name the application is bundled for.
    :param revision: Release version of the bundle.
    :param source_dir: Path to local directory of yaml files to be read
    :param yamls: List of yaml strings to create bundle with
    """
    
    bundle = build_and_verify(source_dir, yamls)

    if bundle is not None:
        with TemporaryDirectory() as temp_dir:
            with open('%s/bundle.yaml' % temp_dir, 'w') as outfile:
                yaml.dump(bundle, outfile, default_flow_style=False)
                outfile.flush()

            PushCmd().push(temp_dir, namespace, repository, revision, token)
    else:
        logger.error("Bundle is invalid. Will not attempt to push.")
        raise ValueError("Resulting bundle is invalid, input yaml is improperly defined.")

def nest(source_dir, registry_dir):
    """Nest takes a flat bundle directory and version nests it to eventually be consumed as part of an operator-registry image build.

    :param source_dir: Path to local directory of yaml files to be read
    :param output_dir: Path of your directory to be populated. If directory does not exist, it will be created.
    """
    
    yaml_files = []

    if source_dir is not None: 
        for filename in os.listdir(source_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(source_dir + "/" + filename) as f:
                    yaml_files.append(f.read())

    with TemporaryDirectory() as temp_dir:
        nest_bundles(yaml_files, registry_dir, temp_dir)
