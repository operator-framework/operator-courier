from distutils.dir_util import copy_tree
import logging
import os
import yaml
import operatorcourier.identify as identify

logger = logging.getLogger(__name__)


def nest_bundles(yaml_files, registry_dir, temp_registry_dir):
    package = {}
    crds = {}
    csvs = []

    errors = []

    # first lets parse all the files
    for yaml_string in yaml_files:
        yaml_type = identify.get_operator_artifact_type(yaml_string)
        if yaml_type == "Package":
            if not package:
                package = yaml.safe_load(yaml_string)
            else:
                errors.append("Multiple packages in directory.")
        if yaml_type == "CustomResourceDefinition":
            crd = yaml.safe_load(yaml_string)
            crd_name = crd["metadata"]["name"]
            crds[crd_name] = crd
        if yaml_type == "ClusterServiceVersion":
            csv = yaml.safe_load(yaml_string)
            csvs.append(csv)

    if len(csvs) == 0:
        errors.append("No csvs in directory.")

    if not package:
        errors.append("No package file in directory.")

    # write the package file
    package_name = package["packageName"]
    with open('%s/%s.package.yaml' % (temp_registry_dir, package_name), 'w') as outfile:
        yaml.dump(package, outfile, default_flow_style=False)
        outfile.flush()

    # now lets create a subdirectory for each version of the csv, and add all the relevant crds to it
    for csv in csvs:
        csv_name = csv["metadata"]["name"]
        version = csv["spec"]["version"]
        csv_folder = temp_registry_dir + "/" + version

        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)

        with open('%s/%s.clusterserviceversion.yaml' % (csv_folder, csv_name), 'w') as outfile:
            yaml.dump(csv, outfile, default_flow_style=False)
            outfile.flush()

        csv_crds = csv["spec"]["customresourcedefinitions"]["owned"]
        for csv_crd in csv_crds:
            crd_name = csv_crd["name"]
            if crd_name in crds:
                crd = crds[crd_name]
                with open('%s/%s.crd.yaml' % (csv_folder, crd_name), 'w') as outfile:
                    yaml.dump(crd, outfile, default_flow_style=False)
                    outfile.flush()
            else:
                errors.append("CRD %s mentioned in CSV %s was not found in directory." % (crd_name, csv_name))

    # if no errors were encountered, lets create the real directory and populate it.
    if len(errors) == 0:
        if not os.path.exists(registry_dir):
            os.makedirs(registry_dir)
        copy_tree(temp_registry_dir, registry_dir)
    else:
        for err in errors:
            logger.error(err)
