import pytest
import operatorcourier.identify as identify
from operatorcourier.errors import OpCourierBadYaml
from testfixtures import LogCapture


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
    ("tests/test_files/empty.yaml"),
    ("tests/test_files/invalid.yaml"),
])
def test_get_operator_artifact_type_assertions(fname):
    with open(fname) as f:
        yaml = f.read()
        result = identify.get_operator_artifact_type(yaml)

    assert result == identify.UNKNOWN_FILE


@pytest.mark.parametrize('fname', [
    "tests/test_files/invalid.malformed.parser.error.yaml",
    "tests/test_files/invalid.malformed.scanner.error.yaml",
])
def test_get_operator_artifact_type_with_invalid_yaml(fname):
    with open(fname) as f:
        yaml = f.read()

    with pytest.raises(OpCourierBadYaml) as e, LogCapture() as logs:
        identify.get_operator_artifact_type(yaml)

    logs.check(('operatorcourier.identify',
                'ERROR',
                'Courier requires valid input YAML files'),)
    assert 'Courier requires valid input YAML files' == str(e.value)
