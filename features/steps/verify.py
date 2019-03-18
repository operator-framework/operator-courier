from behave import step, use_step_matcher
import subprocess

use_step_matcher("re")


@step('operator-courier should be able to verify the VALID input yaml files '
      'in the input directory "(?P<source_dir>.+)"')
def test_verify_the_valid_input_yaml_files_in_the_input_directory(context, source_dir):
    cmd = f'operator-courier verify {source_dir}'
    exit_code = subprocess.check_call(cmd, shell=True)
    assert exit_code == 0


@step(
    'operator-courier should verify that the input yaml files in the input directory '
    '"(?P<source_dir>.+)" is invalid, return a non-zero status, '
    'and log error messages that contain "(?P<error_message>.+)"')
def step_impl(context, source_dir, error_message):
    process = subprocess.Popen(f'operator-courier verify {source_dir}',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code != 0

    outputs = process.stdout.read().decode("utf-8")
    assert error_message in outputs
