from unittest import TestCase
import pytest
import command.identify as identify

@pytest.mark.parametrize('fname,expected', [
("tests/test_files/csv.yaml", "clusterServiceVersions"),
("tests/test_files/crd.yaml", "customResourceDefinitions"),
("tests/test_files/package.yaml", "packages"),
("tests/test_files/invalid.yaml", "invalid"),
("tests/test_files/empty.yaml", "invalid"),
])
def test_get_operator_artifact_type(fname, expected):
    with open(fname) as f:
        yaml = f.read()
        assert identify.get_operator_artifact_type(yaml) == expected
