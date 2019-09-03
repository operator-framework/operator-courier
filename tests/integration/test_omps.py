import pytest
import requests
from os import getenv, path, walk, remove
from random import randint
from zipfile import ZipFile

quay_namespace = getenv('QUAY_NAMESPACE')
quay_access_token = getenv('QUAY_ACCESS_TOKEN')
test_omps_host = getenv('OMPS_HOST')


def setup_module():
    healthz_url = '%s/v2/health/ping' % (test_omps_host)
    res = requests.get(healthz_url)
    assert res.status_code == 200


@pytest.mark.parametrize('source_dir,repository_name', [
    ('tests/test_files/bundles/api/etcd_valid_nested_bundle', 'etcd'),
    ('tests/test_files/bundles/api/valid_flat_bundle', 'marketplace'),
])
def test_push_valid_sources(source_dir, repository_name):
    release_version = '%d.%d.%d' % (randint(0, 99999), randint(0, 99999),
                                    randint(0, 99999))

    zip_path = '%s.zip' % (path.basename(source_dir))
    with ZipFile(zip_path, 'w') as zipper:
        zipdir(source_dir, zipper)

    upload_url = '%s/v2/%s/zipfile/%s' % (test_omps_host, quay_namespace, release_version)
    headers = {'Authorization': quay_access_token}
    files = {'file': open(zip_path, 'rb')}

    res = requests.post(upload_url, files=files, headers=headers)
    assert res.status_code == 200

    ensure_application_release_removed_omps(repository_name, release_version)
    ensure_zipfile_removed(zip_path)


@pytest.mark.parametrize('source_dir,repository_name,release_version,error_message', [
    ('tests/test_files/yaml_source_dir/invalid_yamls_without_package',
     'oneagent',
     '0.0.1',
     'Could not find packageName in manifests.'),
    ('tests/test_files/yaml_source_dir/invalid_yamls_multiple_packages',
     'oneagent',
     '0.0.1',
     'Only 1 package is expected to exist in source root folder.'),
])
def test_push_invalid_sources(source_dir, repository_name,
                              release_version, error_message):
    zip_path = '%s.zip' % (path.basename(source_dir))
    with ZipFile(zip_path, 'w') as zipper:
        zipdir(source_dir, zipper)

    upload_url = '%s/v2/%s/zipfile/%s' % (test_omps_host, quay_namespace, release_version)
    headers = {'Authorization': quay_access_token}
    files = {'file': open(zip_path, 'rb')}

    res = requests.post(upload_url, files=files, headers=headers)
    assert res.status_code != 200
    message = res.json()['message']
    assert error_message in message

    ensure_zipfile_removed(zip_path)


def zipdir(dir, zipf):
    for root, dirs, files in walk(dir):
        for file in files:
            src_path = path.join(root, file)
            dst_path = path.relpath(src_path, dir)
            zipf.write(src_path, dst_path)


def ensure_application_release_removed_omps(repository_name, release_version):
    delete_url = '%s/v2/%s/%s/%s' % (test_omps_host, quay_namespace,
                                     repository_name, release_version)
    headers = {'Authorization': quay_access_token}

    res = requests.delete(delete_url, headers=headers)
    assert res.status_code == 200


def ensure_zipfile_removed(zip_path):
    assert remove(zip_path) is None
