import pytest
import yaml
from operatorcourier import api
from operatorcourier.format import unformat_bundle
from operatorcourier.errors import OpCourierBadBundle


@pytest.mark.parametrize('directory,expected', [
    ("tests/test_files/bundles/api/bundle1",
     "tests/test_files/bundles/api/bundle1/results/bundle.yaml"),
])
def test_make_bundle(directory, expected):
    verified_manifest = api.build_and_verify(source_dir=directory)

    with open(expected, "r") as expected_file:
        expected_bundle = yaml.safe_load(expected_file)
    assert unformat_bundle(verified_manifest.bundle) == unformat_bundle(expected_bundle)
    assert not verified_manifest.nested
    assert hasattr(verified_manifest, 'bundle')


@pytest.mark.parametrize('yaml_files,expected', [
    (
        [
            "tests/test_files/bundles/api/bundle1/crd.yml",
            "tests/test_files/bundles/api/bundle1/csv.yaml",
            "tests/test_files/bundles/api/bundle1/packages.yaml"
        ],
        "tests/test_files/bundles/api/bundle1/results/bundle.yaml"
    ),
])
def test_make_bundle_with_yaml_list(yaml_files, expected):
    yamls = []
    for file in yaml_files:
        with open(file, "r") as yaml_file:
            yamls.append(yaml_file.read())

    verified_manifest = api.build_and_verify(yamls=yamls)

    with open(expected, "r") as expected_file:
        expected_bundle = yaml.safe_load(expected_file)
    assert unformat_bundle(verified_manifest.bundle) == unformat_bundle(expected_bundle)
    assert not verified_manifest.nested
    assert hasattr(verified_manifest, 'bundle')


@pytest.mark.parametrize('yaml_files', [
    ["tests/test_files/bundles/api/bundle1/crd.yml",
     "tests/test_files/bundles/api/bundle1/csv.yaml"]
])
def test_make_bundle_invalid(yaml_files):
    yamls = []
    for file in yaml_files:
        with open(file, "r") as yaml_file:
            yamls.append(yaml_file.read())

    with pytest.raises(OpCourierBadBundle) as e_info:
        api.build_and_verify(yamls=yamls)

    e = e_info.value
    e_msg = "Resulting bundle is invalid, input yaml is improperly defined."
    e_dict = {
        "warnings": [
            "csv metadata.annotations not defined.",
            "csv spec.icon not defined"
        ],
        "errors": ["Bundle does not contain any packages."]
    }
    assert str(e) == e_msg
    assert e.validation_info == e_dict


@pytest.mark.parametrize('nested_source_dir', [
    'tests/test_files/bundles/api/prometheus_valid_nested_bundle',
    'tests/test_files/bundles/api/etcd_valid_nested_bundle',
])
def test_valid_nested_bundles(nested_source_dir):
    verified_manifest = api.build_and_verify(source_dir=nested_source_dir)
    assert verified_manifest.nested


# Made changes to etcdoperator.v0.9.0.clusterserviceversion.yaml and
# removed apiVersion and spec.installModes
@pytest.mark.parametrize('nested_source_dir', [
    'tests/test_files/bundles/api/etcd_invalid_nested_bundle',
])
def test_invalid_nested_bundles(nested_source_dir):
    with pytest.raises(OpCourierBadBundle) as e_info:
        api.build_and_verify(source_dir=nested_source_dir, repository='invalid_repo')

    e = e_info.value
    e_msg = "Resulting bundle is invalid, input yaml is improperly defined."
    expected_errors = {
        'csv apiVersion not defined.',
        'csv spec.installModes not defined',
        'The packageName (etcd) in bundle does not match repository name '
        '(invalid_repo) provided as command line argument.',
        'The packageName (etcd) in bundle does not match repository name '
        '(invalid_repo) provided as command line argument.',
        'The packageName (etcd) in bundle does not match repository name '
        '(invalid_repo) provided as command line argument.',
    }
    assert str(e) == e_msg
    assert set(e.validation_info['errors']) == expected_errors
