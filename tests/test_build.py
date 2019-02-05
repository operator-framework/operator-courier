from unittest import TestCase
import pytest
from operatorcourier.build import BuildCmd


def test_create_bundle():
    paths = ["tests/test_files/csv.yaml", "tests/test_files/crd.yaml", "tests/test_files/package.yaml"]
    yamls = []
    for path in paths:
        with open(path) as f:
            yamls.append(f.read())

    bundle = BuildCmd().build_bundle(yamls)
    assert bool(bundle["data"]["packages"]) == True
    assert bool(bundle["data"]["clusterServiceVersions"]) == True
    assert bool(bundle["data"]["customResourceDefinitions"]) == True
