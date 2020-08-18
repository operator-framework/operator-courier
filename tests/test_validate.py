import yaml
import pytest
from operatorcourier.validate import ValidateCmd
from operatorcourier.format import unformat_bundle


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/noicon.valid.bundle.yaml",
        {'errors': [], 'warnings': [
            'csv metadata.annotations.categories not defined',
            'csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/nocrd.valid.bundle.yaml",
        {'errors': [], 'warnings': [
            'csv spec.icon not defined',
            'csv spec.maturity not defined']}),
    ("tests/test_files/bundles/verification/multiplecrds.bundle.yaml",
        {'errors': [], 'warnings': [
            'csv metadata.annotations.createdAt not defined',
            'csv spec.icon not defined']}),
])
def test_valid_bundles(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert valid is True
    assert validation_results_dict == expected_validation_results_dict


@pytest.mark.parametrize('bundle,expected_validation_results_dict', [
    ("tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml",
        {'errors': ['Bundle does not contain any packages.'],
            'warnings': [
                'csv metadata.annotations.categories not defined',
                'csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/no-data-key.bundle.yaml",
        {'errors': ['Bundle does not contain any clusterServiceVersions.',
                    'Bundle does not contain any packages.'], 'warnings': []}),
    ("tests/test_files/bundles/verification/csvinstallspecnotlists.invalid.bundle.yaml",
        {'errors': ['csv spec.install.spec.deployments should be a list',
                    'csv spec.install.spec.permissions should be a list',
                    'csv spec.install.spec.clusterPermissions should be a list'],
            'warnings': ['csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/"
        "csvmissinginstallattributes.invalid.bundle.yaml",
        {'errors': ['csv spec.install.strategy not defined',
                    'csv spec.install.spec not defined'],
            'warnings': ['csv spec.icon not defined']}),
    ("tests/test_files/bundles/verification/"
        "csvinstallstrategywrongvalue.invalid.bundle.yaml",
        {'errors': ["csv spec.install.strategy must be one of ['deployment']"],
            'warnings': ['csv spec.icon not defined']}),
])
def test_invalid_bundle(bundle, expected_validation_results_dict):
    valid, validation_results_dict = get_validation_results(bundle)
    assert valid is False
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
        valid, _ = ValidateCmd().validate(bundle)

    assert not valid


def get_ui_validation_results(bundle):
    return ValidateCmd(ui_validate_io=True).validate(get_bundle(bundle))


def get_validation_results(bundle):
    return ValidateCmd().validate(get_bundle(bundle))


def get_bundle(bundle):
    with open(bundle) as f:
        bundle = yaml.safe_load(f)
    return unformat_bundle(bundle)


@pytest.mark.parametrize('bundleFile', [
    ('tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/crdmissingpluralfield.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/crdmissingversionfield.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/csvmissingkindfield.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/csvmissingnamefield.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/csvmissingversionfield.invalid.bundle.yaml'),
])
def test_invalid_bundle_missing_fields(bundleFile):
    _test_invalid_bundle(bundleFile)


@pytest.mark.parametrize('bundleFile', [
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch1.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch2.invalid.bundle.yaml'),
    ('tests/test_files/bundles/verification/csvcrdfieldmismatch3.invalid.bundle.yaml'),
])
def test_invalid_bundle_crd_csv_fields_mismatch(bundleFile):
    _test_invalid_bundle(bundleFile)


def _test_invalid_bundle(bundleFile):
    with open(bundleFile) as f:
        bundle = yaml.safe_load(f)
        unformatted_bundle = unformat_bundle(bundle)
        valid, _ = ValidateCmd().validate(unformatted_bundle)
        assert not valid


@pytest.mark.parametrize('file_name', [
    "tests/test_files/bundles/verification/crdversions.invalid.bundle.yaml",
])
def test_invalid_crd_versions_field(file_name):
    with open(file_name) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)
        valid, _ = ValidateCmd().validate(bundle)

    assert not valid


@pytest.mark.parametrize('file_name', [
    "tests/test_files/bundles/verification/crdversions.valid.bundle.yaml",
])
def test_valid_crd_versions_field(file_name):
    with open(file_name) as f:
        bundle = yaml.safe_load(f)
        bundle = unformat_bundle(bundle)
        valid, _ = ValidateCmd().validate(bundle)

    assert valid
