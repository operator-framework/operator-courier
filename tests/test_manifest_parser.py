import pytest
import os
from tempfile import TemporaryDirectory
from distutils.dir_util import copy_tree
from operatorcourier.manifest_parser import filterOutFiles
from operatorcourier.push import BLACK_LIST


@pytest.mark.parametrize('folder_to_filter,expected_output_dir', [
    ("tests/test_files/bundles/flatten/etcd_valid_input_7",
     "tests/test_files/bundles/flatten/etcd_valid_input_7_result")
])
def test_filterOutFiles(folder_to_filter, expected_output_dir):
    with TemporaryDirectory() as output_dir:
        copy_tree(folder_to_filter, output_dir)
        filterOutFiles(output_dir, BLACK_LIST)
        assert _get_dir_file_paths(output_dir) == _get_dir_file_paths(expected_output_dir)


def _get_dir_file_paths(source_dir):
    """
    :param source_dir: the path of the input directory
    :return: a set of relative paths of all files inside input directory and
             its subdirectories
    """
    file_paths = set()

    for root_path, dir_names, file_names in os.walk(source_dir):
        dir_path_relative = os.path.relpath(root_path, source_dir)
        for file_name in file_names:
            file_paths.add(os.path.join(dir_path_relative, file_name))
    return file_paths
