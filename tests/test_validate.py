import yaml
import pytest
from operatorcourier.validate import ValidateCmd
from operatorcourier.format import unformat_bundle
from testfixtures import LogCapture


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/valid.bundle.yaml",
        {'errors': [], 'warnings': ['csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/nocrd.valid.bundle.yaml",
        {'errors': [], 'warnings': ['csv spec.icon not defined',
         'csv spec.maturity not defined']}),
])
def test_valid_bundles(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert valid is True
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml",
        {'errors': ['Bundle does not contain any packages.'],
            'warnings': ['csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/no-data-key.bundle.yaml",
        {'errors': ['Bundle does not contain any clusterServiceVersions.',
                    'Bundle does not contain any packages.'], 'warnings': []}),
])
def test_invalid_bundle(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert valid is False
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
        ("tests/test_files/bundles/verification/valid.bundle.yaml",
            {'errors': [], 'warnings': ['csv spec.icon not defined',
                                        'csv spec.icon not defined. Without this field, '
                                        'the operator will display a default operator '
                                        'framework icon.']}), ])
def test_ui_valid_bundle_io(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_ui_validation_results(bundle)
    assert valid is True
    assert validation_results_dict == expected_validation_results_dict


def get_ui_validation_results(bundle):
    return ValidateCmd(ui_validate_io=True).validate(get_bundle(bundle))


def get_validation_results(bundle):
    return ValidateCmd().validate(get_bundle(bundle))


def get_bundle(bundle):
    with open(bundle) as f:
        bundle = yaml.safe_load(f)
    return unformat_bundle(bundle)


@pytest.mark.parametrize('bundleFile,logInfo', [
    ('tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR', 'Bundle does not contain any packages.')),

    ('tests/test_files/bundles/verification/crdmissingkindfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR', 'crd spec.names.kind not defined.')),
    ('tests/test_files/bundles/verification/crdmissingpluralfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR', 'crd spec.names.plural not defined.')),
    ('tests/test_files/bundles/verification/crdmissingversionfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR', 'crd spec.version not defined.')),

    ('tests/test_files/bundles/verification/csvmissingkindfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'kind not defined for item in spec.customresourcedefinitions.')),
    ('tests/test_files/bundles/verification/csvmissingnamefield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'name not defined for item in spec.customresourcedefinitions.')),
    ('tests/test_files/bundles/verification/csvmissingversionfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'version not defined for item in spec.customresourcedefinitions.')),
])
def test_invalid_bundle_missing_fields(bundleFile, logInfo):
    _test_invalid_bundle_with_log(bundleFile, logInfo)


@pytest.mark.parametrize('bundleFile,logInfo', [
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch1.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'CRD.spec.names.kind does not match CSV.spec.crd.owned.kind')),
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch2.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'CRD.spec.version does not match CSV.spec.crd.owned.version')),
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch3.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      '`CRD.spec.names.plural`.`CRD.spec.group` does not match CSV.spec.crd.owned.name')),
])
def test_invalid_bundle_crd_csv_fields_mismatch(bundleFile, logInfo):
    _test_invalid_bundle_with_log(bundleFile, logInfo)


def _test_invalid_bundle_with_log(bundleFile, logInfo):
    with open(bundleFile) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)
        module, level, message = logInfo[0], logInfo[1], logInfo[2]
        with LogCapture() as logs:
            valid, _ = ValidateCmd().validate(bundle)
        assert not valid

        # check if the input log info is present among all logs captured
        logs.check_present(
            (module, level, message),
        )
