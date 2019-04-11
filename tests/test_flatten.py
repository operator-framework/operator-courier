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

        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.6.1/'
         'etcdoperator.clusterserviceversion.yaml',
         'etcdoperator.clusterserviceversion-v0.6.1.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.9.0/'
         'etcdoperator.v0.9.0.clusterserviceversion.yaml',
         'etcdoperator.v0.9.0.clusterserviceversion-v0.9.0.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.9.2/'
         'etcdoperator.v0.9.2.clusterserviceversion.yaml',
         'etcdoperator.v0.9.2.clusterserviceversion-v0.9.2.yaml'),

        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.9.2/etcdrestore.crd.yaml',
         'etcdrestore.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.9.2/etcdbackup.crd.yaml',
         'etcdbackup.crd.yaml'),
        ('tests/test_files/bundles/flatten/etcd_valid_input_3/0.9.2/etcdcluster.crd.yaml',
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
    # if the source_dir is already flat, just return files
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
])
def test_flatten_with_valid_bundle(input_dir, expected_flattened_file_paths):
    actual_flattened_file_paths = flatten.get_flattened_files_info(input_dir)
    assert set(expected_flattened_file_paths) == set(actual_flattened_file_paths)
