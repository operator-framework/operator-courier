import yaml
from operatorcourier.validate import ValidateCmd
from operatorcourier.format import unformat_bundle


def test_valid_bundles():
    bundles = ["tests/test_files/bundles/verification/valid.bundle.yaml", "tests/test_files/bundles/verification/nocrd.valid.bundle.yaml"]
    for bundle in bundles:
        with open(bundle) as f:
            bundle = yaml.safe_load(f)
            bundle = unformat_bundle(bundle)
            valid = ValidateCmd().validate(bundle)
            assert valid is True


def test_invalid_bundle():
    bundles = ["tests/test_files/bundles/verification/nopkg.invalid.bundle.yaml"]
    for bundle in bundles:
        with open(bundle) as f:
            bundle = yaml.safe_load(f)
            bundle = unformat_bundle(bundle)
            valid = ValidateCmd().validate(bundle)
            assert valid is False


def test_ui_valid_bundle_io():
    bundles = ["tests/test_files/bundles/verification/valid.bundle.yaml"]
    for bundle in bundles:
        with open(bundle) as f:
            bundle = yaml.safe_load(f)
            bundle = unformat_bundle(bundle)
            valid = ValidateCmd(ui_validate_io=True).validate(bundle)
            assert valid is True
