import os
import pytest
import subprocess
import yaml
from tempfile import TemporaryDirectory


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
    "tests/test_files/yaml_source_dir/valid_yamls_with_multiple_crds"
])
def test_verify_with_output_file(source_dir):
    with TemporaryDirectory() as temp_dir:
        output = os.path.join(temp_dir, "output.yaml")
        verify_command = f'operator-courier verify {source_dir} --output={output}'
        process = subprocess.Popen(verify_command,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        exit_code = process.wait()
        assert exit_code == 0

        file_created = os.path.isfile(output)
        assert file_created

        with open(output, 'r') as actual_output_file:
            actual_output = yaml.safe_load(actual_output_file)
            assert actual_output['data'] is not None


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
