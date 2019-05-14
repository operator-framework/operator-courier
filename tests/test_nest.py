import pytest
import os
from tempfile import TemporaryDirectory
from operatorcourier.nest import nest_bundles


@pytest.mark.parametrize('folder_to_nest,expected_output_dir', [
    ("tests/test_files/bundles/nest/flat_bundle1",
     "tests/test_files/bundles/nest/flat_bundle1_result"),

    ("tests/test_files/bundles/nest/flat_bundle2_without_crds",
     "tests/test_files/bundles/nest/flat_bundle2_without_crds_result"),

    ("tests/test_files/bundles/nest/nested_bundle1",
     "tests/test_files/bundles/nest/nested_bundle1_result"),
])
def test_nest(folder_to_nest, expected_output_dir):
    with TemporaryDirectory() as output_dir:
        nest_bundles(folder_to_nest, output_dir)
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
