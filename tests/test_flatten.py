import pytest
import operatorcourier.flatten as flatten


@pytest.mark.parametrize('input_dir,expected_flattened_file_paths', [
    ('tests/test_files/bundles/flatten/etcd_valid_input_1', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_1/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.6.1/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.6.1.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.9.0/'
         'etcdoperator.v0.9.0.clusterserviceversion.yaml',
         'etcdoperator.v0.9.0.clusterserviceversion-v0.9.0.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.9.2/'
         'etcdoperator.v0.9.2.clusterserviceversion.yaml',
         'etcdoperator.v0.9.2.clusterserviceversion-v0.9.2.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.9.0/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.9.0/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_1/0.9.2/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
    ]),
    ('tests/test_files/bundles/flatten/etcd_valid_input_2', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_2/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.6.1/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.6.1.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.9.0/'
         'etcdoperator.v0.9.0.clusterserviceversion.yaml',
         'etcdoperator.v0.9.0.clusterserviceversion-v0.9.0.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.9.2/'
         'etcdoperator.v0.9.2.clusterserviceversion.yaml',
         'etcdoperator.v0.9.2.clusterserviceversion-v0.9.2.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.9.0/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.6.1/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_2/0.6.1/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
    ]),
    ('tests/test_files/bundles/flatten/etcd_valid_input_3', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.61/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.61.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.90/'
         'etcdoperator.v0.9.0.clusterserviceversion.yaml',
         'etcdoperator.v0.9.0.clusterserviceversion-v0.90.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.92/'
         'etcdoperator.v0.9.2.clusterserviceversion.yaml',
         'etcdoperator.v0.9.2.clusterserviceversion-v0.92.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.92/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.92/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.92/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
    ]),
    # duplicate CSV names in different versions will be appended with
    # the version at the end of the basename
    ('tests/test_files/bundles/flatten/etcd_valid_input_4', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_4/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.6.1/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.6.1.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.9.0/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.9.0.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.9.2/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.9.2.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.9.2/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.9.2/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_4/0.9.2/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
    ]),
    # if the source_dir is already flat (the "random folder" is ignored),
    # just return files in source root directory
    ('tests/test_files/bundles/flatten/etcd_valid_input_5', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_5/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_5/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_5/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        (('tests/test_files/bundles/flatten/etcd_valid_input_5/etcdoperator.'
          'clusterserviceversion.yaml'),
         'etcdoperator.clusterserviceversion.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_5/etcd.package.yaml',
         'etcd.package.yaml'),
    ]),
    # treat the source directory as in nested format when there is at least 1 valid
    # manifest folder, even if there are valid CSVs specific in root directory
    ('tests/test_files/bundles/flatten/etcd_valid_input_6', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_6/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_6/0.9/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.9.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_6/0.9/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_6/0.9/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_6/0.9/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
    ]),
    # Ignore extraneous files
    ('tests/test_files/bundles/flatten/etcd_valid_input_7', [
        ('tests/test_files/bundles/flatten/etcd_valid_input_7/etcd.package.yaml',
         'etcd.package.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_7/0.9/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.9.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_7/0.9/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_7/0.9/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_7/0.9/etcdcluster.crd.yaml',
         'etcdcluster.crd.yaml'),
    ]),
])
def test_flatten_with_valid_bundle(input_dir, expected_flattened_file_paths):
    actual_flattened_file_paths = flatten.get_flattened_files_info(input_dir)
    assert set(expected_flattened_file_paths) == set(actual_flattened_file_paths)
