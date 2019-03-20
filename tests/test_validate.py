import yaml
import pytest
from operatorcourier.validate import ValidateCmd
from operatorcourier.format import unformat_bundle
import operatorcourier.schema
from testfixtures import LogCapture


@pytest.mark.parametrize('schema', [
    ('CustomResourceDefinition'),
    ('ClusterServiceVersion')
])
def test_schema(schema):
    getattr(operatorcourier.schema, schema)().check_schema()


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/noicon.valid.bundle.yaml",
        {'errors': [], 'warnings': [
            "csv.metadata.annotations: 'categories' is not defined",
            "csv.spec: 'icon' is not defined"]}),
    ("tests/test_files/bundles/verification/nocrd.valid.bundle.yaml",
        {'errors': [], 'warnings': [
            "csv.spec: 'icon' is not defined",
            "csv.spec: 'maturity' is not defined"]}),
    ("tests/test_files/bundles/verification/"
     "customresourcedefinitions.missing.valid.bundle.yaml",
        {'errors': [], 'warnings': []}),
])
def test_valid_bundles(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert valid
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml",
        {'errors': ['Bundle does not contain any packages.'],
         'warnings': ["csv.metadata.annotations: 'categories' is not defined",
                      "csv.spec: 'icon' is not defined"]}),
    ("tests/test_files/bundles/verification/no-data-key.bundle.yaml",
        {'errors': ['Bundle does not contain any clusterServiceVersions.',
                    'Bundle does not contain any packages.'], 'warnings': []}),
    ("tests/test_files/bundles/verification/csvinstallspecnotlists.invalid.bundle.yaml",
        {'errors': ["csv.spec.install.spec.deployments: "
                    "'This is not a list' is not of type 'array'",
                    "csv.spec.install.spec.permissions: "
                    "'Definitely not a list' is not of type 'array'",
                    "csv.spec.install.spec.clusterPermissions: "
                    "'This is not an array' is not of type 'array'"],
            'warnings': ["csv.spec: 'icon' is not defined"]}),
    ("tests/test_files/bundles/verification/"
        "csvmissinginstallattributes.invalid.bundle.yaml",
        {'errors': ["csv.spec.install: 'strategy' is a required property",
                    "csv.spec.install: 'spec' is a required property"],
            'warnings': ["csv.spec: 'icon' is not defined"]}),
    ("tests/test_files/bundles/verification/"
        "csvinstallstrategywrongvalue.invalid.bundle.yaml",
        {'errors': ["csv.spec.install.strategy: "
                    "'foodeployment' is not one of ['deployment']"],
            'warnings': ["csv.spec: 'icon' is not defined"]}),
    ("tests/test_files/bundles/verification/alm-examples.invalid.bundle.yaml",
        {'errors': ["csv.metadata.annotations.alm-examples: "
                    "'{\\n  bad-example\\n}' is not a 'jsonString'"],
         'warnings': []}),
    ("tests/test_files/bundles/verification/wrongcrd.invalid.bundle.yaml",
        {'errors': ["csv.spec.customresourcedefinitions.owned[0].name: "
                    "'operatorsources.marketplace.example.com' is not one of "
                    "['catalogsourceconfigs.marketplace.redhat.com', "
                    "'operatorsources.marketplace.redhat.com']"],
         'warnings': []}),
    ("tests/test_files/bundles/verification/owned.name.missing.invalid.bundle.yaml",
        {'errors': ["csv.spec.customresourcedefinitions.owned[0]: "
                    "'name' is a required property"],
         'warnings': []}),
    ("tests/test_files/bundles/verification/owned.missing.invalid.bundle.yaml",
        {'errors': ["csv.spec.customresourcedefinitions: "
                    "'owned' is a required property"],
         'warnings': []}),
])
def test_invalid_bundle(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert not valid
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
        ("tests/test_files/bundles/verification/valid.bundle.yaml",
            {'errors': [], 'warnings': []}), ])
def test_ui_valid_bundle_io(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_ui_validation_results(bundle)
    assert valid is True
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
        ("tests/test_files/bundles/verification/ui.invalid.bundle.yaml",
            {'errors': [
                "csv.spec.links must be a list of name & url pairs.",
                "spec.version invalid is not a valid semver "
                "(example of a valid semver is: 1.0.12)",
                "metadata.annotations.capabilities invalid "
                "is not a valid capabilities level",
                "spec.icon[0].mediatype image/invalid is not "
                "a valid mediatype. It must be one of \"image/gif\", "
                "\"image/jpeg\", \"image/png\", \"image/svg+xml\"",
                "category invalid is not a valid category",
                "UI validation failed to verify that required fields "
                "for operatorhub.io are properly formatted."
                ],
                'warnings': []}), ])
def test_ui_invalid_bundle_io(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_ui_validation_results(bundle)
    assert valid is False
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('file_name,correct_repo_name', [
    ("tests/test_files/bundles/verification/valid.bundle.yaml", 'marketplace'),
    ("tests/test_files/bundles/verification/nocrd.valid.bundle.yaml", 'svcat'),
])
def test_valid_bundles_with_package_name_and_repo_name_match(file_name,
                                                             correct_repo_name):
    with open(file_name) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)
        valid, _ = ValidateCmd().validate(bundle, repository=correct_repo_name)
        assert valid


@pytest.mark.parametrize('file_name,wrong_repo_name', [
    ("tests/test_files/bundles/verification/valid.bundle.yaml", 'wrong-repo-name'),
    ("tests/test_files/bundles/verification/nocrd.valid.bundle.yaml", 'wrong-repo-name'),
])
def test_valid_bundles_with_package_name_and_repo_name_mismatch(file_name,
                                                                wrong_repo_name):
    with open(file_name) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)
        valid, _ = ValidateCmd().validate(bundle, repository=wrong_repo_name)
        assert not valid


@pytest.mark.parametrize('file_name', [
    "tests/test_files/bundles/verification/multiplepkgs.invalid.bundle.yaml",
])
def test_valid_bundles_with_multiple_packages(file_name):
    with open(file_name) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)

    with LogCapture() as logs:
        valid, _ = ValidateCmd().validate(bundle)

    assert not valid
    logs.check_present(('operatorcourier.validate',
                        'ERROR',
                        'Only 1 package is expected to exist per bundle, but got 2.'))


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
     ('operatorcourier.validate', 'ERROR',
      'crd.spec.names: \'kind\' is a required property')),
    ('tests/test_files/bundles/verification/crdmissingpluralfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'crd.spec.names: \'plural\' is a required property')),
    ('tests/test_files/bundles/verification/crdmissingversionfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'crd.spec: \'version\' is a required property')),

    ('tests/test_files/bundles/verification/csvmissingkindfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'csv.spec.customresourcedefinitions.owned[1]: \'kind\' is a required property')),
    ('tests/test_files/bundles/verification/csvmissingnamefield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'csv.spec.customresourcedefinitions.owned[0]: \'name\' is a required property')),
    ('tests/test_files/bundles/verification/csvmissingversionfield.invalid.bundle.yaml',
     ('operatorcourier.validate', 'ERROR',
      'csv.spec.customresourcedefinitions.owned[0]: \'version\' is a required property')),
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
