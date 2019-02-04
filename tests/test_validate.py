import pytest
import yaml
from command.validate import ValidateCmd

#use same variable name twice!

def test_valid_bundles():
    bundles = ["tests/test_files/bundles/verification/valid.bundle.yaml", "tests/test_files/bundles/verification/nocrd.valid.bundle.yaml"]
    for bundle in bundles:
        with open(bundle) as f:
            bundle = yaml.safe_load(f)
            valid = ValidateCmd().validate(bundle)
            assert valid == True

def test_invalid_bundle():
    bundles = ["tests/test_files/bundles/verification/invalid.bundle.yaml"]
    for bundle in bundles:
        with open(bundle) as f:
            bundle = yaml.safe_load(f)
            valid = ValidateCmd().validate(bundle)
            assert valid == False
