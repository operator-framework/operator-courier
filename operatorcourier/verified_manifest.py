import os
import copy
import logging
import json
from operatorcourier.build import BuildCmd
from operatorcourier.validate import ValidateCmd
from operatorcourier.errors import OpCourierBadBundle
from operatorcourier.format import format_bundle
from operatorcourier.manifest_parser import \
    is_manifest_folder, get_csvs_pkg_info_from_root, get_crd_csv_files_info


logger = logging.getLogger(__name__)
FLAT_KEY = '__flat__'


class VerifiedManifest:
    @property
    def bundle(self):
        if self.nested:
            raise AttributeError('VerifiedManifest does not have the bundle property '
                                 'in nested cases.')
        return format_bundle(self.bundle_dict)

    @property
    def validation_dict(self):
        return copy.deepcopy(self.__validation_dict)

    def __init__(self, source_dir, yamls, ui_validate_io, repository):
        self.nested = False

        if yamls:
            yaml_strings_with_metadata = self._set_empty_filepaths(yamls)
            manifests = {FLAT_KEY: yaml_strings_with_metadata}
        else:
            manifests = self.get_manifests_info(source_dir)

        self.bundle_dict = None
        self.__validation_dict = \
            self.get_validation_dict_from_manifests(manifests, ui_validate_io, repository)
        self.is_valid = False if self.__validation_dict['errors'] else True

    def _set_empty_filepaths(self, yamls):
        yaml_strings_with_metadata = []
        for yaml_string in yamls:
            yaml_tuple = ("", yaml_string)
            yaml_strings_with_metadata.append(yaml_tuple)

        return yaml_strings_with_metadata

    def get_manifests_info(self, source_dir):
        """
        Given a source directory, this method returns a dict containing all
        operator manifest file information, grouped by subfolder name if the
        manifest directory structure is nested.

        :param source_dir: Path to local directory of operator manifests, which can be
                           in either flat or nested format
        :return: A dictionary object where the key is the folder name of the operator
                 manifest, and the value is a list of yaml strings of manifest files

                 FLAT_KEY is used as key if the directory structure is flat
        """
        # MANIFEST_DIR_NAME => manifest_files_content
        # FLAT_KEY is used as key to indicate the flat directory structure
        manifests = {}

        root_path, dir_names, root_dir_files = next(os.walk(source_dir))
        csvs_path_and_content, pkg_path_and_content \
            = get_csvs_pkg_info_from_root(source_dir)

        dir_paths = [os.path.join(source_dir, dir_name) for dir_name in dir_names]
        manifest_paths = list(filter(lambda x: is_manifest_folder(x), dir_paths))

        # if there is at least 1 valid manifest folder, we treat the directory layout as
        # nested, and add all manifest files from each version folder to manifests dict

        # nested layout: add package to each manifest dict entry
        if manifest_paths:
            logger.info('The source directory is in nested structure.')
            self.nested = True
            for manifest_path in manifest_paths:
                manifest_dir_name = os.path.basename(manifest_path)

                crd_files_info, csv_files_info = get_crd_csv_files_info(manifest_path)
                manifests[manifest_dir_name] = crd_files_info + csv_files_info
            for manifest_dir_name in manifests:
                manifests[manifest_dir_name].append(pkg_path_and_content)
        # flat layout: collect all valid manifest files and add to FLAT_KEY entry
        elif pkg_path_and_content and csvs_path_and_content:
            logger.info('The source directory is in flat structure.')
            crd_files_info, csv_files_info = get_crd_csv_files_info(root_path)
            files_info = [pkg_path_and_content]
            files_info.extend(crd_files_info + csv_files_info)

            manifests[FLAT_KEY] = files_info
        else:
            msg = 'The source directory structure is not in valid flat or nested format,'\
                  'because no valid CSV file is found in root or manifest directories.'
            logger.error(msg)
            raise OpCourierBadBundle(msg, {})

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
        for version, manifest_files_info in manifests.items():
            bundle_dict = BuildCmd().build_bundle(manifest_files_info)
            if version != FLAT_KEY:
                logger.info("Parsing version: %s", version)
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
