from unittest import TestCase
import pytest
import yaml
from operatorcourier import api

@pytest.mark.parametrize('directory,expected', [
("tests/test_files/bundles/api/bundle1", "tests/test_files/bundles/api/bundle1/results/bundle.yaml"),
])
def test_make_bundle(directory, expected):
    bundle = api.build_and_verify(source_dir=directory)

    with open(expected, "r") as expected_file:
        expected_bundle = yaml.safe_load(expected_file)
        assert bundle == expected_bundle

@pytest.mark.parametrize('yaml_files,expected', [
(["tests/test_files/bundles/api/bundle1/crd.yml",
"tests/test_files/bundles/api/bundle1/csv.yaml",
"tests/test_files/bundles/api/bundle1/packages.yaml"],
"tests/test_files/bundles/api/bundle1/results/bundle.yaml"),
])
def test_make_bundle_with_yaml_list(yaml_files, expected):
    yamls = []
    for file in yaml_files:
        with open(file, "r") as yaml_file:
            yamls.append(yaml_file.read())

    bundle = api.build_and_verify(yamls=yamls)

    with open(expected, "r") as expected_file:
        expected_bundle = yaml.safe_load(expected_file)
        assert bundle == expected_bundle
