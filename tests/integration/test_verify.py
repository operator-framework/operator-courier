import pytest
import subprocess
from tempfile import TemporaryDirectory
from os.path import join, isfile
from json import loads


@pytest.mark.parametrize('source_dir', [
    "tests/test_files/yaml_source_dir/valid_yamls_with_multiple_crds",
    "tests/test_files/yaml_source_dir/valid_yamls_with_single_crd",
    "tests/test_files/yaml_source_dir/valid_yamls_without_crds",
])
def test_verify_valid_sources(source_dir):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code == 0


@pytest.mark.parametrize('source_dir', [
    "tests/test_files/bundles/api/valid_flat_bundle",
    "tests/test_files/bundles/api/valid_flat_bundle_with_random_folder",
    "tests/test_files/bundles/api/etcd_valid_nested_bundle",
    "tests/test_files/bundles/api/etcd_valid_nested_bundle_with_random_folder",
    "tests/test_files/bundles/api/prometheus_valid_nested_bundle",
    "tests/test_files/bundles/api/prometheus_valid_nested_bundle_2",
])
def test_verify_valid_nested_sources(source_dir):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code == 0


@pytest.mark.parametrize('source_dir', [
    "tests/test_files/bundles/api/etcd_invalid_nested_bundle",
])
def test_verify_invalid_nested_sources(source_dir):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code != 0


@pytest.mark.parametrize('source_dir', [
    "tests/test_files/bundles/api/valid_flat_bundle_with_random_folder",
    "tests/test_files/bundles/api/etcd_valid_nested_bundle_with_random_folder",
    "tests/test_files/bundles/api/prometheus_valid_nested_bundle_2",
])
def test_verify_valid_nested_sources_with_output(source_dir):
    with TemporaryDirectory() as temp_dir:
        outfile_path = join(temp_dir, "output.json")
        process = subprocess.Popen(f'operator-courier verify {source_dir} '
                                   f'--validation-output {outfile_path}',
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        exit_code = process.wait()
        assert isfile(outfile_path)
        with open(outfile_path, 'r') as f:
            validation_json = loads(f.read())

    assert exit_code == 0
    assert not validation_json['errors']


@pytest.mark.parametrize('source_dir', [
    "tests/test_files/bundles/api/etcd_invalid_nested_bundle",
])
def test_verify_invalid_nested_sources_with_output(source_dir):
    with TemporaryDirectory() as temp_dir:
        outfile_path = join(temp_dir, "output.json")
        process = subprocess.Popen(f'operator-courier verify {source_dir} '
                                   f'--validation-output {outfile_path}',
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        exit_code = process.wait()
        assert isfile(outfile_path)
        with open(outfile_path, 'r') as f:
            validation_json = loads(f.read())

    assert exit_code != 0
    assert validation_json['errors']


@pytest.mark.parametrize('source_dir,error_message', [
    ("tests/test_files/yaml_source_dir/invalid_yamls_without_package",
     "ERROR:operatorcourier.manifest_parser:Bundle does not contain any packages."),
    ("tests/test_files/yaml_source_dir/invalid_yamls_multiple_packages",
     "ERROR:operatorcourier.manifest_parser:"
     "Only 1 package is expected to exist in source root folder."),
])
def test_verify_invalid_sources(source_dir, error_message):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code != 0

    outputs = process.stdout.read().decode("utf-8")
    assert error_message in outputs


@pytest.mark.parametrize('source_dir', [
    "valid_yamls_with_single_crd",
])
def test_verify_valid_sources_root_dir(source_dir):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               cwd="./tests/test_files/yaml_source_dir/")
    exit_code = process.wait()
    assert exit_code == 0
