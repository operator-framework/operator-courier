import pytest
import yaml
from pathlib import Path
from testfixtures import LogCapture

from operatorcourier.bundle import OperatorBundle
from operatorcourier.format import unformat_bundle
from operatorcourier.errors import OpCourierBadBundle


@pytest.fixture
def valid_bundle_dir():
    return 'tests/test_files/bundles/api/bundle1'


@pytest.fixture
def valid_bundle_result(valid_bundle_dir):
    path = Path(valid_bundle_dir) / 'results/bundle.yaml'
    with path.open() as f:
        return unformat_bundle(yaml.safe_load(f))


@pytest.fixture
def valid_bundle_yamls(valid_bundle_dir):
    d = Path(valid_bundle_dir)
    yaml_files = [d / 'crd.yml', d / 'csv.yaml', d / 'packages.yaml']
    return [f.read_text() for f in yaml_files]


@pytest.fixture
def valid_bundle_validation_info(valid_bundle_dir):
    path = Path(valid_bundle_dir) / 'results/validation.json'
    with path.open() as f:
        return yaml.safe_load(f)


@pytest.fixture
def invalid_bundle_yamls(valid_bundle_dir):
    d = Path(valid_bundle_dir)
    yaml_files = [d / 'crd.yml', d / 'csv.yaml']
    return [f.read_text() for f in yaml_files]


# -- Fixtures above, tests below ----------------------------------------------


def test_bundle_is_invalid_by_default():
    bundle = OperatorBundle()
    assert not bundle.valid
    assert bundle.validation_info is None


def test_build_bundle_from_dir(valid_bundle_dir, valid_bundle_result):
    bundle = OperatorBundle.from_directory(valid_bundle_dir)
    assert bundle.data_copy() == valid_bundle_result


def test_build_bundle_from_yamls(valid_bundle_yamls, valid_bundle_result):
    bundle = OperatorBundle.from_yaml_data(valid_bundle_yamls)
    assert bundle.data_copy() == valid_bundle_result


def test_build_valid_bundle(valid_bundle_dir, valid_bundle_validation_info):
    bundle = OperatorBundle.from_directory(valid_bundle_dir)
    assert bundle.valid
    assert bundle.validation_info == valid_bundle_validation_info


def test_build_invalid_bundle(invalid_bundle_yamls):
    bundle = OperatorBundle.from_yaml_data(invalid_bundle_yamls)
    assert not bundle.valid
    assert ('Bundle does not contain any packages.'
            in bundle.validation_info['errors'])


def test_validate_valid_bundle(valid_bundle_dir, valid_bundle_validation_info):
    bundle = OperatorBundle.from_directory(valid_bundle_dir)
    bundle._valid = False
    bundle._validation_info = None

    bundle.validate()

    assert bundle.valid
    assert bundle.validation_info == valid_bundle_validation_info


def test_validate_invalid_bundle(invalid_bundle_yamls):
    bundle = OperatorBundle.from_yaml_data(invalid_bundle_yamls)
    bundle._valid = True
    bundle._validation_info = None

    bundle.validate()

    assert not bundle.valid
    assert ('Bundle does not contain any packages.'
            in bundle.validation_info['errors'])


def test_cannot_modify_bundle_data(valid_bundle_dir, valid_bundle_result):
    bundle = OperatorBundle.from_directory(valid_bundle_dir)
    data = bundle.data_copy()

    data['data']['clusterServiceVersions'][0] = None
    assert bundle._data == valid_bundle_result

    data.clear()
    assert bundle._data == valid_bundle_result


def test_cannot_push_invalid_bundle(invalid_bundle_yamls):
    bundle = OperatorBundle.from_yaml_data(invalid_bundle_yamls)

    with pytest.raises(OpCourierBadBundle) as exc_info, LogCapture() as logs:
        bundle.push('a', 'b', 'c', 'd')

    msg = str(exc_info.value)
    assert msg == 'Resulting bundle is invalid, input yaml is improperly defined.'
    logs.check_present(('operatorcourier.bundle',
                        'ERROR',
                        'Bundle failed validation.'))


def test_write_validation_info(valid_bundle_dir, valid_bundle_validation_info):
    bundle = OperatorBundle.from_directory(valid_bundle_dir)
    bundle.validate()

    out_file = Path(valid_bundle_dir) / 'results/tmp.json'
    bundle.write_validation_info(out_file)

    with out_file.open() as f:
        output = yaml.safe_load(f)

    out_file.unlink()

    assert output == valid_bundle_validation_info
