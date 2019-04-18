import pytest
import subprocess


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


@pytest.mark.parametrize('source_dir,error_message', [
    ("tests/test_files/yaml_source_dir/invalid_yamls_without_package",
     "ERROR:operatorcourier.validate:Bundle does not contain any packages."),
    ("tests/test_files/yaml_source_dir/invalid_yamls_multiple_packages",
     "ERROR:operatorcourier.validate:"
     "Only 1 package is expected to exist per bundle, but got 2."),
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
