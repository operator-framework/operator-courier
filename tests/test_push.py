import base64
import tarfile

import pytest
import os
from tempfile import TemporaryDirectory
from distutils.dir_util import copy_tree
from operatorcourier.push import PushCmd


@pytest.mark.parametrize('bundle_dir', [
    "tests/test_files/bundles/api/etcd_valid_nested_bundle"
])
def test_create_base64_bundle(bundle_dir):
    with TemporaryDirectory() as scratch:
        directory_name = "directory-abcd"
        # make a subdirectory with a known name so that the bundle is always the same
        inpath = os.path.join(scratch, directory_name)
        os.mkdir(inpath)

        copy_tree(bundle_dir, inpath)
        out = PushCmd()._create_base64_bundle(inpath, "repo")

        outpath = os.path.join(scratch, "out")
        os.mkdir(outpath)

        # write the output tar
        tardata = base64.b64decode(out)
        tarfile_name = os.path.join(outpath, "bundle.tar.gz")
        with open(tarfile_name, "wb") as bundle:
            bundle.write(tardata)

        # uncompress the bundle
        with tarfile.open(tarfile_name) as bundle:
            bundle.extractall(path=outpath)

        outfiles = os.listdir(outpath)

        # ensure the surrouding directory was packed into the tar archive
        assert directory_name in outfiles
