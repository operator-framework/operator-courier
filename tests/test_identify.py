from unittest import TestCase
import pytest
import operatorcourier.identify as identify

@pytest.mark.parametrize('fname,expected', [
("tests/test_files/csv.yaml", "ClusterServiceVersion"),
("tests/test_files/crd.yaml", "CustomResourceDefinition"),
("tests/test_files/package.yaml", "Package"),
])
def test_get_operator_artifact_type(fname, expected):
    with open(fname) as f:
        yaml = f.read()
        assert identify.get_operator_artifact_type(yaml) == expected


@pytest.mark.parametrize('fname', [
("tests/test_files/invalid.yaml"),
("tests/test_files/empty.yaml"),
])
def test_get_operator_artifact_type_assertions(fname):
    with open(fname) as f:
        yaml = f.read()
        with pytest.raises(ValueError):
            identify.get_operator_artifact_type(yaml)
