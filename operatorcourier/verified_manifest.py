import os
import logging
import json
from operatorcourier.build import BuildCmd
from operatorcourier.validate import ValidateCmd
from operatorcourier.errors import OpCourierBadBundle
from operatorcourier.format import format_bundle
from operatorcourier import identify

logger = logging.getLogger(__name__)
FLAT_KEY = '__flat__'


class VerifiedManifest:
    @property
    def bundle(self):
        if self.nested:
            raise AttributeError('VerifiedManifest does not have the bundle property '
                                 'in nested cases.')
        return format_bundle(self.bundle_dict)

    def __init__(self, source_dir, yamls, ui_validate_io, repository):
        if yamls:
            manifests = dict(FLAT_KEY=yamls)
        else:
            manifests = self.get_manifests_info(source_dir)

        self.nested = len(manifests) > 1
        self.bundle_dict = None
        self.__validation_dict = \
            self.get_validation_dict_from_manifests(manifests, ui_validate_io, repository)
        self.is_valid = False if self.__validation_dict['errors'] else True

    def get_manifest_files_content(self, file_paths):
        """
        Given a list of file paths, the function returns a list of strings containing
        file content in all yaml files.
        :param file_paths: a list of file paths
        :return: a list of strings containing file content in all yaml files
        """
        manifests_content = []
        for file_path in file_paths:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                with open(file_path) as f:
                    manifests_content.append(f.read())
        return manifests_content

    def get_manifests_info(self, source_dir):
        """
        Given a source directory OR a list of yaml files. The function returns a dict
        containing all operator bundle file information grouped by version. Note that only
        one of source_dir or yamls can be specified.

        :param source_dir: Path to local directory of operator bundles, which can be
                           either flat or nested
        :param yamls: A list of yaml strings to create bundle with
        :return: A dictionary object where the key is the semantic version of each bundle,
                 and the value is a list of yaml strings of operator bundle files.
                 FLAT_KEY is used as key if the directory structure is flat
        """
        # VERSION => manifest_files_content
        # FLAT_KEY is used as key to indicate the flat directory structure
        manifests = {}

        root_path, dir_names, root_dir_files = next(os.walk(source_dir))
        # flat directory
        if not dir_names:
            manifests[FLAT_KEY] = self.get_manifest_files_content(
                [os.path.join(root_path, file) for file in root_dir_files])
        # nested
        else:
            # add all manifest files from each version folder to manifests dict
            for version_dir in dir_names:
                version_dir_path = os.path.join(root_path, version_dir)
                _, _, version_dir_files = next(os.walk(version_dir_path))
                file_paths = [os.path.join(version_dir_path, file)
                              for file in version_dir_files]
                manifests[version_dir] = self.get_manifest_files_content(file_paths)
            # get the package file from root dir and add to each version of manifest
            package_content = None
            for root_dir_file in root_dir_files:
                with open(os.path.join(root_path, root_dir_file), 'r') as f:
                    file_content = f.read()
                if identify.get_operator_artifact_type(file_content) == 'Package':
                    # ensure only 1 package is found in root directory
                    if package_content:
                        msg = 'There should be only 1 package file defined ' \
                              'in the source directory.'
                        logging.error(msg)
                        raise OpCourierBadBundle(msg, {})
                    package_content = file_content
            if not package_content:
                msg = 'No package file exists in the nested bundle.'
                logging.error(msg)
                raise OpCourierBadBundle(msg, {})
            for version in manifests:
                manifests[version].append(package_content)
        return manifests

    def get_validation_dict_from_manifests(self, manifests, ui_validate_io=False,
                                           repository=None):
        """
        Given a dict of manifest files where the key is the version of the manifest
        (or FLAT_KEY if the manifest files are not grouped by version), the function
        returns a dict containing validation info (warnings/errors).

        :param manifests: a dict of manifest files where the key is the version
        of the manifest (or FLAT_KEY if the manifest files are not grouped by version)
        :param ui_validate_io: the ui_validate_io flag specified from CLI
        :param repository: the repository value specified from CLI
        :return: a dict containing validation info (warnings/errors).
        """
        bundle_dict = None
        # validate on all bundles files and combine log messages
        validation_dict = ValidateCmd(ui_validate_io).validation_json
        for version, manifest_files_content in manifests.items():
            bundle_dict = BuildCmd().build_bundle(manifest_files_content)
            if version != FLAT_KEY:
                logging.info("Parsing version: %s", version)
            _, validation_dict_temp = ValidateCmd(ui_validate_io, self.nested) \
                .validate(bundle_dict, repository)
            for log_level, msg_list in validation_dict_temp.items():
                validation_dict[log_level].extend(msg_list)

        if not self.nested:
            self.bundle_dict = bundle_dict

        return validation_dict

    def write_validation_to_file(self, file_path):
        with open(file_path, 'w') as f:
            f.write(json.dumps(self.__validation_dict))
            f.write('\n')
