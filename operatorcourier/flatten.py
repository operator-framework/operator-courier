import logging
import os
from yaml import safe_load, MarkedYAMLError
from typing import Dict, Tuple
from shutil import copyfile
import semver
from operatorcourier import identify
from operatorcourier.errors import OpCourierBadBundle, OpCourierBadYaml
from operatorcourier.manifest_parser \
    import is_manifest_folder, get_csvs_pkg_info_from_root, is_yaml_file

logger = logging.getLogger(__name__)


def flatten_bundles(source_dir: str, dest_dir: str):
    file_paths_to_copy = get_flattened_files_info(source_dir)
    for (src_file_path, new_file_name) in file_paths_to_copy:
        copyfile(src_file_path, os.path.join(dest_dir, new_file_name))


def get_flattened_files_info(source_dir: str) -> [(str, str)]:
    """
    :param source_dir: Path of the directory containing different versions
    of operator bundles (CRD, CSV, package) in separate version directories
    :return: A list of tuples where in each tuple, the first element is
    the source file path to be copied to the flattened directory, and the second is
    the new file name to be used in the file copy.
    """

    # get package content and check if CSV exists in source_dir root, and
    # process all subdirectories and filter those that do not contain valid manifest files
    root_path, dir_names, root_dir_files = next(os.walk(source_dir))
    csvs_path_and_content, pkg_path_and_content \
        = get_csvs_pkg_info_from_root(source_dir)

    dir_paths = [os.path.join(source_dir, dir_name) for dir_name in dir_names]
    manifest_paths = list(filter(lambda x: is_manifest_folder(x), dir_paths))

    # nested layout
    if manifest_paths:
        file_paths_to_copy = []  # [ (SRC_FILE_PATH, NEW_FILE_NAME) ]

        crd_dict = {}  # { CRD_NAME => (VERSION, CRD_PATH) }
        csv_paths = []

        for manifest_path in manifest_paths:
            folder_semver = get_folder_semver(manifest_path)
            if not folder_semver:
                continue
            parse_manifest_folder(manifest_path, folder_semver,
                                  csv_paths, crd_dict)

        # add package in source_dir
        package_path = pkg_path_and_content[0]
        file_paths_to_copy.append((package_path, os.path.basename(package_path)))

        # add all CRDs with the latest version
        for _, crd_path in crd_dict.values():
            file_paths_to_copy.append((crd_path, os.path.basename(crd_path)))

        # add all CSVs
        for csv_file_name, csv_entries in create_csv_dict(csv_paths).items():
            for (version, csv_path) in csv_entries:
                basename, ext = os.path.splitext(csv_file_name)
                file_paths_to_copy.append((csv_path, f'{basename}-v{version}{ext}'))

        return file_paths_to_copy
    # flat layout
    elif pkg_path_and_content and csvs_path_and_content:
        logger.info('The source directory is already flat.')
        # just return files from dir as they are already flat
        return [(os.path.join(source_dir, name), name) for name in root_dir_files]

    msg = 'The source directory structure is not in valid flat or nested format,' \
          'because no valid CSV file is found in root or manifest directories.'
    logger.error(msg)
    raise OpCourierBadBundle(msg, {})


def get_folder_semver(folder_path: str):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path) or not is_yaml_file(item_path):
            continue

        with open(item_path, 'r') as f:
            file_content = f.read()

        if identify.get_operator_artifact_type(file_content) == 'ClusterServiceVersion':
            try:
                csv_version = safe_load(file_content)['spec']['version']
            except MarkedYAMLError:
                msg = f'{item} is not a valid YAML file.'
                logger.error(msg)
                raise OpCourierBadYaml(msg)
            except KeyError:
                msg = f'{item} is not a valid CSV file as "spec.version" ' \
                      f'field is required'
                logger.error(msg)
                raise OpCourierBadBundle(msg, {})
            return csv_version

    return None


def parse_manifest_folder(manifest_path: str, folder_semver: str,
                          csv_paths: list, crd_dict: Dict[str, Tuple[str, str]]):
    """
    Parse the version folder of the bundle and collect information of CSV and CRDs
    in the bundle

    :param manifest_path: The path of the manifest folder containing bundle files
    :param folder_semver: The semantic version of the current folder
    :param csv_paths: A list of CSV file paths inside version folders
    :param crd_dict: dict that contains CRD info collected from different version folders,
    where the key is the CRD name, and the value is a tuple where the first element is
    the version of the bundle, and the second is the path of the CRD file
    """
    logger.info('Parsing folder %s for operator version %s',
                os.path.basename(manifest_path), folder_semver)

    contains_csv = False

    for item in os.listdir(manifest_path):
        item_path = os.path.join(manifest_path, item)

        if not os.path.isfile(item_path):
            logger.warning('Ignoring %s as it is not a regular file.', item)
            continue
        if not is_yaml_file(item_path):
            logger.warning('Ignoring %s as the file does not end with .yaml or .yml',
                           item_path)
            continue

        with open(item_path, 'r') as f:
            file_content = f.read()

        yaml_type = identify.get_operator_artifact_type(file_content)

        if yaml_type == 'ClusterServiceVersion':
            contains_csv = True
            csv_paths.append(item_path)
        elif yaml_type == 'CustomResourceDefinition':
            try:
                crd_name = safe_load(file_content)['metadata']['name']
            except MarkedYAMLError:
                msg = "Courier requires valid input YAML files"
                logger.error(msg)
                raise OpCourierBadYaml(msg)
            except KeyError:
                msg = f'{item} is not a valid CRD file as "metadata.name" ' \
                      f'field is required'
                logger.error(msg)
                raise OpCourierBadBundle(msg, {})
            # create new CRD type entry if not found in dict
            if crd_name not in crd_dict:
                crd_dict[crd_name] = (folder_semver, item_path)
            # update the CRD type entry with the file with the newest version
            elif semver.compare(folder_semver, crd_dict[crd_name][0]) > 0:
                crd_dict[crd_name] = (crd_dict[crd_name][0], item_path)

    if not contains_csv:
        msg = 'This version directory does not contain any valid CSV file.'
        logger.error(msg)
        raise OpCourierBadBundle(msg, {})


# parse all CSVs and ensure those with same names are handled
def create_csv_dict(csv_paths: list) -> dict:
    csv_dict = {}  # { CSV_FILE_NAME => [ (v1, csv_path_1), ... , (vn, csv_path_n) ] }
    for csv_path in csv_paths:
        version_folder_path, csv_file_name = os.path.split(csv_path)
        version = os.path.basename(version_folder_path)
        val = (version, csv_path)
        csv_dict.setdefault(csv_file_name, []).append(val)
    return csv_dict
