from distutils.dir_util import copy_tree
import logging
import os
import yaml
from shutil import copyfile
from tempfile import TemporaryDirectory
from operatorcourier import identify
from operatorcourier.errors import OpCourierBadBundle
from operatorcourier.manifest_parser import \
    is_manifest_folder, get_csvs_pkg_info_from_root, get_crd_csv_files_info, \
    CRD_STR, CSV_STR, PKG_STR


logger = logging.getLogger(__name__)


def nest_bundles(source_dir, output_dir):
    root_path, dir_names, root_dir_files = next(os.walk(source_dir))
    csvs_info, pkg_info = get_csvs_pkg_info_from_root(source_dir)

    dir_paths = [os.path.join(source_dir, dir_name) for dir_name in dir_names]
    manifest_paths = list(filter(lambda x: is_manifest_folder(x), dir_paths))

    # nested layout
    if manifest_paths:
        logger.warning('The source directory is already nested.')

        # extract paths of package file in root dir and
        # valid CRD/CSV files from subdirectories, and ignore irrelevant ones
        manifest_files_path = [pkg_info[0]]

        for manifest_path in manifest_paths:
            crds_info, csvs_info = get_crd_csv_files_info(manifest_path)
            crd_csv_file_paths = [file_info[0] for file_info in (crds_info + csvs_info)]
            manifest_files_path.extend(crd_csv_file_paths)

        # copy all manifest files to output_dir with folder structure preserved
        os.makedirs(output_dir, exist_ok=True)
        for file_path in manifest_files_path:
            file_path_relative = os.path.relpath(file_path, source_dir)
            output_file_path = os.path.join(output_dir, file_path_relative)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            copyfile(file_path, output_file_path)

    # flat layout
    elif csvs_info and pkg_info:
        # extract all valid manifest (CRD, CSV, PKG) files from root
        # and make nested bundles
        crds_info, csvs_info = get_crd_csv_files_info(source_dir)
        with TemporaryDirectory() as temp_dir:
            manifest_files_content = [pkg_info[1]]
            manifest_files_content.extend(
                [file_content for (_, file_content) in (crds_info + csvs_info)])

            nest_flat_bundles(manifest_files_content, output_dir, temp_dir)
    else:
        msg = 'The source directory structure is not in valid flat or nested format,' \
              'because no valid CSV file is found in root or manifest directories.'
        logger.error(msg)
        raise OpCourierBadBundle(msg, {})


def nest_flat_bundles(manifest_files_content, output_dir, temp_registry_dir):
    package = {}
    crds = {}
    csvs = []

    errors = []

    # first lets parse all the files
    for yaml_string in manifest_files_content:
        yaml_type = identify.get_operator_artifact_type(yaml_string)
        if yaml_type == PKG_STR:
            if not package:
                package = yaml.safe_load(yaml_string)
            else:
                errors.append("Multiple packages in directory.")
        if yaml_type == CRD_STR:
            crd = yaml.safe_load(yaml_string)
            if "metadata" in crd and "name" in crd["metadata"]:
                crd_name = crd["metadata"]["name"]
                crds[crd_name] = crd
            else:
                errors.append("CRD has no `metadata.name` field defined")
        if yaml_type == CSV_STR:
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

            csv_path = os.path.join(csv_folder, f'{csv_name}.clusterserviceversion.yaml')
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
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        copy_tree(temp_registry_dir, output_dir)
    else:
        for err in errors:
            logger.error(err)
