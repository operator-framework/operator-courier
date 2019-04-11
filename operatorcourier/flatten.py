import logging
import os
from yaml import safe_load, MarkedYAMLError
from typing import Dict, Tuple
from shutil import copyfile
import semver
from operatorcourier import identify
from operatorcourier import errors

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
    the new file name to be used in the file copy. The function returns an empty list if
    the source_dir is already flat
    """

    # extract package file and version folders from source_dir
    root, folder_names, file_names = next(os.walk(source_dir))
    if not folder_names:
        logger.info('The source directory is already flat.')
        # just return files from dir as they are already flat
        return [
            (os.path.join(root, name), name)
            for name in file_names
        ]

    file_paths_to_copy = []  # [ (SRC_FILE_PATH, NEW_FILE_NAME) ]

    crd_dict = {}  # { CRD_NAME => (VERSION, CRD_PATH) }
    csv_paths = []

    for version_folder_name in folder_names:
        parse_version_folder(source_dir, version_folder_name, csv_paths, crd_dict)

    # add package in source_dir
    package_path = get_package_path(source_dir, file_names)
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


def parse_version_folder(base_dir: str, version_folder_name: str,
                         csv_paths: list, crd_dict: Dict[str, Tuple[str, str]]):
    """
    Parse the version folder of the bundle and collect information of CSV and CRDs
    in the bundle

    :param base_dir: Path of the base directory where the version folder is located
    :param version_folder_name: The name of the version folder containing bundle files
    :param csv_paths: A list of CSV file paths inside version folders
    :param crd_dict: dict that contains CRD info collected from different version folders,
    where the key is the CRD name, and the value is a tuple where the first element is
    the version of the bundle, and the second is the path of the CRD file
    """
    # parse each version folder and parse CRD, CSV files
    try:
        semver.parse(version_folder_name)
    except ValueError:
        logger.warning("Ignoring %s as it is not a valid semver. "
                       "See https://semver.org for the semver specification.",
                       version_folder_name)
        return

    logger.info('Parsing folder: %s...', version_folder_name)

    contains_csv = False
    version_folder_path = os.path.join(base_dir, version_folder_name)

    for item in os.listdir(os.path.join(base_dir, version_folder_name)):
        item_path = os.path.join(version_folder_path, item)

        if not os.path.isfile(item_path):
            logger.warning('Ignoring %s as it is not a regular file.', item)
            continue
        if not is_yaml_file(item_path):
            logging.warning('Ignoring %s as the file does not end with .yaml or .yml',
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
                raise errors.OpCourierBadYaml(msg)
            except KeyError:
                msg = f'{item} is not a valid CRD file as "metadata.name" ' \
                      f'field is required'
                logger.error(msg)
                raise errors.OpCourierBadBundle(msg, {})
            # create new CRD type entry if not found in dict
            if crd_name not in crd_dict:
                crd_dict[crd_name] = (version_folder_name, item_path)
            # update the CRD type entry with the file with the newest version
            elif semver.compare(version_folder_name, crd_dict[crd_name][0]) > 0:
                crd_dict[crd_name] = (crd_dict[crd_name][0], item_path)

    if not contains_csv:
        msg = 'This version directory does not contain any valid CSV file.'
        logger.error(msg)
        raise errors.OpCourierBadBundle(msg, {})


def get_package_path(base_dir: str, file_names_in_base_dir: list) -> str:
    packages = []

    # add package file to file_paths_to_copy
    # only 1 package yaml file is expected in file_names
    for file_name in file_names_in_base_dir:
        file_path = os.path.join(base_dir, file_name)
        if not is_yaml_file(file_path):
            logging.warning('Ignoring %s as the file does not end with .yaml or .yml',
                            file_path)
            continue

        with open(file_path, 'r') as f:
            file_content = f.read()
        if identify.get_operator_artifact_type(file_content) != 'Package':
            logger.warning('Ignoring %s as it is not a valid package file.', file_name)
        elif not packages:
            packages.append(file_path)
        else:
            msg = f'The input source directory expects only 1 valid package file.'
            logger.error(msg)
            raise errors.OpCourierBadBundle(msg, {})

    if not packages:
        msg = f'The input source directory expects at least 1 valid package file.'
        logger.error(msg)
        raise errors.OpCourierBadBundle(msg, {})

    return packages[0]


# parse all CSVs and ensure those with same names are handled
def create_csv_dict(csv_paths: list) -> dict:
    csv_dict = {}  # { CSV_FILE_NAME => [ (v1, csv_path_1), ... , (vn, csv_path_n) ] }
    for csv_path in csv_paths:
        version_folder_path, csv_file_name = os.path.split(csv_path)
        version = os.path.basename(version_folder_path)
        val = (version, csv_path)
        csv_dict.setdefault(csv_file_name, []).append(val)
    return csv_dict


def is_yaml_file(file_path: str) -> bool:
    yaml_ext = ['.yaml', '.yml']
    return os.path.splitext(file_path)[1] in yaml_ext
