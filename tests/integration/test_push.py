import pytest
import subprocess
from os import getenv
from random import randint

import requests

quay_namespace = getenv('QUAY_NAMESPACE')
quay_access_token = getenv('QUAY_ACCESS_TOKEN')


@pytest.mark.parametrize('source_dir,repository_name', [
    ('tests/test_files/yaml_source_dir/valid_yamls_with_multiple_crds',
     'marketplace'),
    ('tests/test_files/yaml_source_dir/valid_yamls_with_single_crd',
     'oneagent'),
    ('tests/test_files/yaml_source_dir/valid_yamls_without_crds',
     'svcat'),
])
def test_push_valid_sources(source_dir, repository_name):
    release_version = f"{randint(0,99999)}.{randint(0,99999)}.{randint(0,99999)}"

    cmd = f'operator-courier push {source_dir} {quay_namespace} ' \
          f"{repository_name} {release_version} '{quay_access_token}'"
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code == 0
    ensure_application_release_removed(repository_name, release_version)


def ensure_application_release_removed(repository_name, release_version):
    api = f'https://quay.io/cnr/api/v1/packages/' \
          f'{quay_namespace}/{repository_name}/{release_version}/helm'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': quay_access_token
    }
    res = requests.delete(api, headers=headers)
    assert res.status_code == 200


@pytest.mark.parametrize('source_dir,repository_name,release_version,error_message', [
    ('tests/test_files/yaml_source_dir/invalid_yamls_without_package',
     'oneagent',
     '0.0.1',
     'ERROR:operatorcourier.manifest_parser:Bundle does not contain any packages.'),
    ('tests/test_files/yaml_source_dir/invalid_yamls_multiple_packages',
     'oneagent',
     '0.0.1',
     'ERROR:operatorcourier.manifest_parser:'
     'Only 1 package is expected to exist in source root folder.'),
    ('tests/test_files/yaml_source_dir/valid_yamls_with_single_crd',
     'wrong-repo-name',
     '0.0.1',
     'ERROR: The packageName (oneagent) in bundle does not match '
     'repository name (wrong-repo-name) provided as command line argument.'),
])
def test_push_invalid_sources(source_dir, repository_name,
                              release_version, error_message):
    cmd = f'operator-courier push {source_dir} {quay_namespace} ' \
          f"{repository_name} {release_version} '{quay_access_token}'"
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    exit_code = process.wait()
    assert exit_code != 0

    outputs = process.stdout.read().decode('utf-8')
    assert error_message in outputs
