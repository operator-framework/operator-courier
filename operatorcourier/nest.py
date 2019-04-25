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
            if "metadata" in crd and "name" in crd["metadata"]:
                crd_name = crd["metadata"]["name"]
                crds[crd_name] = crd
            else:
                errors.append("CRD has no `metadata.name` field defined")
        if yaml_type == "ClusterServiceVersion":
            csv = yaml.safe_load(yaml_string)
            csvs.append(csv)

    if len(csvs) == 0:
        errors.append("No csvs in directory.")

    if not package:
        errors.append("No package file in directory.")

    # write the package file
    if "packageName" in package:
        package_name = package["packageName"]
        packagefile_name = os.path.join(temp_registry_dir, '%s.package.yaml'
                                        % package_name)
        with open(packagefile_name, 'w') as outfile:
            yaml.dump(package, outfile, default_flow_style=False)
            outfile.flush()

        # now lets create a subdirectory for each version of the csv,
        # and add all the relevant crds to it
        for csv in csvs:
            if "metadata" not in csv:
                errors.append("CSV has no `metadata` field defined")
                continue
            if "name" not in csv["metadata"]:
                errors.append("CSV has no `metadata.name` field defined")
                continue
            csv_name = csv["metadata"]["name"]

            if "spec" not in csv:
                errors.append("CSV %s has no `spec` field defined" % csv_name)
                continue
            if "version" not in csv["spec"]:
                errors.append("CSV %s has no `spec.version` field defined" % csv_name)
                continue
            version = csv["spec"]["version"]
            csv_folder = temp_registry_dir + "/" + version

            if not os.path.exists(csv_folder):
                os.makedirs(csv_folder)

            csv_path = '%s/%s.clusterserviceversion.yaml' % (csv_folder, csv_name)
            with open(csv_path, 'w') as outfile:
                yaml.dump(csv, outfile, default_flow_style=False)
                outfile.flush()

            if "customresourcedefinitions" in csv["spec"]:
                if "owned" in csv["spec"]["customresourcedefinitions"]:
                    csv_crds = csv["spec"]["customresourcedefinitions"]["owned"]
                    for csv_crd in csv_crds:
                        if "name" not in csv_crd:
                            errors.append("CSV %s has an owned CRD without a `name`"
                                          "field defined" % csv_name)
                            continue
                        crd_name = csv_crd["name"]
                        if crd_name in crds:
                            crd = crds[crd_name]
                            crdfile_name = os.path.join(csv_folder, '%s.crd.yaml'
                                                        % crd_name)
                            with open(crdfile_name, 'w') as outfile:
                                yaml.dump(crd, outfile, default_flow_style=False)
                                outfile.flush()
                        else:
                            errors.append("CRD %s mentioned in CSV %s was not found"
                                          "in directory." % (crd_name, csv_name))
    else:
        errors.append("Package file has no `packageName` field defined")

    # if no errors were encountered, lets create the real directory and populate it.
    if len(errors) == 0:
        if not os.path.exists(registry_dir):
            os.makedirs(registry_dir)
        copy_tree(temp_registry_dir, registry_dir)
    else:
        for err in errors:
            logger.error(err)
