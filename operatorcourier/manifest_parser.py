import os
import logging
from typing import Tuple, List
from operatorcourier.errors import OpCourierBadBundle
from operatorcourier import identify


logger = logging.getLogger(__name__)
CRD_STR = 'CustomResourceDefinition'
CSV_STR = 'ClusterServiceVersion'
PKG_STR = 'Package'


def is_manifest_folder(folder_path):
    """
    :param folder_path: the path of the input folder
    :return: True if the folder contains valid operator manifest files (at least
             1 valid CSV file), False otherwise
    """
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path):
            continue
        if is_yaml_file(item_path):
            with open(item_path) as f:
                file_content = f.read()
            if CSV_STR == identify.get_operator_artifact_type(file_content):
                return True

    folder_name = os.path.basename(folder_path)
    logger.warning('Ignoring folder "%s" as it is not a valid manifest '
                   'folder', folder_name)
    return False


def get_crd_csv_files_info(folder_path: str) -> Tuple[List[Tuple], List[Tuple]]:
    """
    Given a folder path, the method returns the CRD and CSV files info parsed from the
    input directory.
    :param folder_path: the path of the input folder
    :return: CRD and CSV files info parsed from the input directory. Each files_info
             is a list of tuples, where each tuple contains two elements, namely
             the file path and its content
    """
    crd_files_info, csv_files_info = [], []

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path):
            continue
        if is_yaml_file(item_path):
            with open(item_path) as f:
                file_content = f.read()
            file_type = identify.get_operator_artifact_type(file_content)

            if file_type == CRD_STR:
                crd_files_info.append((item_path, file_content))
            elif file_type == CSV_STR:
                csv_files_info.append((item_path, file_content))

    return crd_files_info, csv_files_info


def get_csvs_pkg_info_from_root(source_dir: str) -> Tuple[List[Tuple], Tuple]:
    """
    Given a source directory path, the method returns the CSVs and package file info
    parsed from the input directory.
    :param source_dir: the path of the input source folder
    :return: CSVs and package file info parsed from the input directory.
             csvs_info is a list of tuples whereas pkg_info is a single tuple, and
             each tuple contains two elements, namely the file path and its content
    """
    root_path, dir_names, root_dir_files = next(os.walk(source_dir))
    root_file_paths = [os.path.join(root_path, file) for file in root_dir_files]

    # [(CSV1_PATH, CSV1_CONTENT), ..., (CSVn_PATH, CSVn_CONTENT)]
    csvs_info_list = []
    # (PKG_PATH, PKG_CONTENT)
    pkg_info = None

    # check if package / csv is present in the source dir root, and
    # populate the above two info variables
    for root_file_path in root_file_paths:
        if is_yaml_file(root_file_path):
            with open(root_file_path) as f:
                file_content = f.read()
            file_type = identify.get_operator_artifact_type(file_content)
            if file_type == CSV_STR:
                csvs_info_list.append((root_file_path, file_content))
            elif file_type == PKG_STR:
                if pkg_info:
                    msg = 'Only 1 package is expected to exist in source root folder.'
                    logger.error(msg)
                    raise OpCourierBadBundle(msg, {})
                pkg_info = (root_file_path, file_content)

    if not pkg_info:
        msg = 'Bundle does not contain any packages.'
        logger.error(msg)
        raise OpCourierBadBundle(msg, {})

    return csvs_info_list, pkg_info


def is_yaml_file(file_path):
    yaml_ext = ['.yaml', '.yml']
    return os.path.splitext(file_path)[1] in yaml_ext


# removes files_names from folder_path and all subdirectories
def filterOutFiles(folder_path, file_names):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path):
            filterOutFiles(item_path, file_names)
        else:
            if item in file_names:
                os.remove(item_path)
    return
