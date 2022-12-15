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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(bundle, path=outpath)

        outfiles = os.listdir(outpath)

        # ensure the surrouding directory was packed into the tar archive
        assert directory_name in outfiles
