import os
import logging
from operatorcourier.errors import OpCourierBadBundle
from operatorcourier import identify


logger = logging.getLogger(__name__)
CRD_KEY = 'CustomResourceDefinition'
CSV_KEY = 'ClusterServiceVersion'


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
            if CSV_KEY == identify.get_operator_artifact_type(file_content):
                return True

    folder_name = os.path.basename(folder_path)
    logger.warning('Ignoring folder "%s" as it is not a valid manifest '
                   'folder', folder_name)
    return False


def get_crd_csv_files_content(folder_path):
    """
    Given a folder path, the method returns a dict containing manifest files
    content grouped by CRD and CSV key.
    :param folder_path: the path of the input folder
    :return: a dict where the key is either  'ClusterServiceVersion' or
             'CustomResourceDefinition', and the value is a list of the valid
             CSV and CRD files content
    """
    crd_csv_files_content = {}
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path):
            continue
        if is_yaml_file(item_path):
            with open(item_path) as f:
                file_content = f.read()
            file_type = identify.get_operator_artifact_type(file_content)
            if file_type in {CRD_KEY, CSV_KEY}:
                crd_csv_files_content.setdefault(file_type, []).append(file_content)
    return crd_csv_files_content


def get_package_csv_info_from_root(source_dir):
    root_path, dir_names, root_dir_files = next(os.walk(source_dir))
    root_file_paths = [os.path.join(root_path, file) for file in root_dir_files]

    # check if package / csv is present in the source dir root
    contains_csv = False
    package_content = None
    for root_file_path in root_file_paths:
        if is_yaml_file(root_file_path):
            with open(root_file_path) as f:
                file_content = f.read()
            file_type = identify.get_operator_artifact_type(file_content)
            if file_type == 'ClusterServiceVersion':
                contains_csv = True
            elif file_type == 'Package':
                if package_content:
                    msg = 'Only 1 package is expected to exist in source root folder.'
                    logger.error(msg)
                    raise OpCourierBadBundle(msg, {})
                package_content = file_content

    if not package_content:
        msg = 'Bundle does not contain any packages.'
        logger.error(msg)
        raise OpCourierBadBundle(msg, {})
    return package_content, contains_csv


def is_yaml_file(file_path):
    yaml_ext = ['.yaml', '.yml']
    return os.path.splitext(file_path)[1] in yaml_ext
