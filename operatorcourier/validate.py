import collections
import logging
import json
import semver
import yaml

import validators as v

from .const_io import (
    general_required_fields,
    metadata_required_fields,
    metadata_annotations_required_fields,
    spec_required_fields)

log_info = {'current_manifest_file': ''}
logger = logging.getLogger(__name__)
logger.propagate = False
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s [%(current_manifest_file)s]')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger = logging.LoggerAdapter(logger, log_info)


class ValidateCmd():
    dataKey = "data"
    metadataKey = "metadata"
    crdKey = "customResourceDefinitions"
    csvKey = "clusterServiceVersions"
    pkgsKey = "packages"

    def __init__(self, ui_validate_io=False, nested=False):
        self.ui_validate_io = ui_validate_io
        self.nested = nested
        self.validation_json = dict(
            warnings=[],
            errors=[],
        )
        pass

    def _log_warning(self, message, *args, **kwargs):
        """_log_warning prints the message to the logger as a warning
        and appends it to a dictionary that can be printed to the
        screen for automation purposes
         :param message: The message to log
        """
        self.validation_json['warnings'].append(message % args)
        logger.warning(message, *args, **kwargs)

    def _log_error(self, message, *args, **kwargs):
        """_log_error prints the message to the logger as an error
        and appends it to a dictionary that can be printed to the
        screen for automation purposes
         :param message: The message to log
        """
        self.validation_json['errors'].append(message % args)
        logger.error(message, *args, **kwargs)

    def get_filename_from_metadata(self, metadata, yaml_dict):
        """
        :param yaml_dict: The yaml dictionary associated with a filename
        :return: Filename associated with a yaml dictionary
        """
        filename = ""
        hashed_key = hash(yaml.dump(yaml_dict))
        if hashed_key in metadata["filenames"]:
            filename = metadata["filenames"][hashed_key]
        return filename

    def validate(self, bundle, repository=None):
        """validate takes a bundle as a dictionary and returns a boolean value that
        describes if the bundle is valid. It also logs verification information when
        there are invalid sections in the bundle.

        :param bundle: Dictionary of bundle value
        :param repository: Repository name for the application
        :param nested: The input source is in nested structure or not
        """
        logger.info("Validating bundle.")

        return self._bundle_validation(bundle, repository), self.validation_json

    def _bundle_validation(self, bundle, repository=None):
        validationDict = dict()

        if self.dataKey not in bundle:
            self._log_error("Bundle does not contain base data field.")
            # break here because there's nothing else to learn
            return False

        bundleData = bundle[self.dataKey]

        validationDict[self.crdKey] = self._type_validation(bundle, self.crdKey,
                                                            self._crd_validation, False)
        validationDict[self.csvKey] = self._type_validation(bundle, self.csvKey,
                                                            self._csv_validation, True)
        validationDict[self.pkgsKey] = self._type_validation(bundle, self.pkgsKey,
                                                             self._pkgs_validation, True)
        if self.ui_validate_io:
            validationDict[self.csvKey] &= self._type_validation(
                bundle, self.csvKey, self._ui_validation_io, True)
        if validationDict[self.pkgsKey] and repository is not None:
            packageName = bundleData['packages'][0]['packageName']
            if repository != packageName:
                self._log_error('The packageName (%s) in bundle does not match '
                                'repository name (%s) provided as command line argument.',
                                packageName, repository)
                validationDict[self.pkgsKey] = False

        valid = True
        for value in validationDict.values():
            if value is False:
                valid = False

        return valid

    def _crd_validation(self, bundle):
        logger.info("Validating custom resource definitions.")
        valid = True

        bundle_metadata = bundle[self.metadataKey]
        bundleData = bundle[self.dataKey]
        crds = bundleData[self.crdKey]

        for crd in crds:
            crd_file_name = self.get_filename_from_metadata(bundle_metadata, crd)
            log_info['current_manifest_file'] = crd_file_name

            if "metadata" in crd:
                if "name" in crd["metadata"]:
                    logger.info("Evaluating crd %s", crd["metadata"]["name"])
                else:
                    self._log_error("crd metadata.name not defined.")
                    valid = False
            else:
                self._log_error("crd metadata not defined.")
                valid = False

            if "apiVersion" not in crd:
                self._log_error("crd apiVersion not defined.")
                valid = False

            if "spec" not in crd:
                self._log_error("crd spec not defined.")
                valid = False
            else:
                if "names" not in crd['spec']:
                    self._log_error("crd spec.names not defined.")
                    valid = False
                else:
                    if "kind" not in crd['spec']['names']:
                        self._log_error("crd spec.names.kind not defined.")
                        valid = False
                    if "plural" not in crd['spec']['names']:
                        self._log_error("crd spec.names.plural not defined.")
                        valid = False
                if "group" not in crd['spec']:
                    self._log_error("crd spec.group not defined.")
                    valid = False
                if (
                    "versions" not in crd['spec'] and
                    "version" not in crd['spec']
                ):
                    self._log_error(
                        "crd spec.version or spec.versions not defined."
                    )
                    valid = False
                if "versions" in crd['spec']:
                    if not len(crd['spec']['versions']) > 0:
                        self._log_error("crd spec.versions is empty.")
                        valid = False
                    else:
                        for ver in crd['spec']['versions']:
                            if (
                                "name" not in ver or
                                "served" not in ver or
                                "storage" not in ver
                            ):
                                self._log_error(
                                    "crd spec.versions contains an invalid "
                                    "CustomResourceDefinitionVersion."
                                )
                                valid = False
                        if "version" in crd['spec']:
                            if (
                                "name" in crd['spec']['version'][0] and
                                crd['spec']['version'][0]['name'] !=
                                crd['spec']['version']
                            ):
                                self._log_error(
                                    "crd spec.version and spec.versions are "
                                    "defined but spec.versions[0].name "
                                    "doesn't match spec.version."
                                )
                                valid = False
                        storage_version_list = [
                            v for v in crd['spec']['versions']
                            if "storage" in v and v['storage'] is True
                        ]
                        if len(storage_version_list) != 1:
                            self._log_error(
                                "crd spec.version should contain exactly "
                                "one version flagged as storage version."
                            )
                            valid = False
        return valid

    def _csv_validation(self, bundle):
        valid = True
        logger.info("Validating cluster service versions.")

        bundle_metadata = bundle[self.metadataKey]
        bundleData = bundle[self.dataKey]
        csvs = bundleData[self.csvKey]

        for csv in csvs:
            csv_file_name = self.get_filename_from_metadata(bundle_metadata, csv)
            log_info['current_manifest_file'] = csv_file_name

            if "metadata" in csv:
                if self._csv_metadata_validation(csv["metadata"]) is False:
                    valid = False
            else:
                self._log_error("csv metadata not defined.")
                valid = False

            if "apiVersion" not in csv:
                self._log_error("csv apiVersion not defined.")
                valid = False

            if "spec" in csv:
                if self._csv_spec_validation(csv["spec"], bundleData) is False:
                    valid = False
            else:
                self._log_error("csv spec not defined.")
                valid = False

        return valid

    def _csv_spec_validation(self, spec, bundleData):
        valid = True
        validCrdVersions = collections.defaultdict(list)
        warnSpecList = ["displayName", "description", "icon",
                        "version", "provider", "maturity"]

        for item in warnSpecList:
            if item not in spec:
                self._log_warning("csv spec.%s not defined" % item)

        if "installModes" not in spec:
            self._log_error("csv spec.installModes not defined")
            valid = False

        if "install" in spec:
            if self._csv_spec_install_validation(spec["install"]) is False:
                valid = False
        else:
            self._log_error("csv spec.install not defined")
            valid = False

        if "customresourcedefinitions" in spec:
            customresourcedefinitions = spec["customresourcedefinitions"]

            crdList = []
            for crd in bundleData[self.crdKey]:
                try:
                    name = crd["metadata"]["name"]
                    crdList.append(name)
                except KeyError:
                    pass

            if "owned" not in customresourcedefinitions:
                self._log_error("spec.customresourcedefinitions.owned"
                                "not defined for csv")
                return False

            for csvOwnedCrd in customresourcedefinitions["owned"]:
                if "name" not in csvOwnedCrd:
                    self._log_error("name not defined for item in "
                                    "spec.customresourcedefinitions.")
                    valid = False
                elif csvOwnedCrd["name"] not in crdList:
                    self._log_error("custom resource definition %s referenced in csv "
                                    "not defined in root list of crds",
                                    csvOwnedCrd["name"])
                    valid = False

                if "kind" not in csvOwnedCrd:
                    self._log_error("kind not defined for item in "
                                    "spec.customresourcedefinitions.")
                    valid = False
                if "version" not in csvOwnedCrd:
                    self._log_error("version not defined for item in "
                                    "spec.customresourcedefinitions.")
                    valid = False

                for crd in bundleData[self.crdKey]:
                    if 'name' not in csvOwnedCrd:
                        continue
                    if 'metadata' not in crd or 'name' not in crd['metadata']:
                        continue
                    if csvOwnedCrd['name'] != crd['metadata']['name']:
                        continue

                    if 'kind' in csvOwnedCrd:
                        if 'spec' in crd:
                            if 'names' in crd['spec']:
                                if 'kind' in crd['spec']['names']:
                                    if csvOwnedCrd['kind'] != \
                                            crd['spec']['names']['kind']:
                                        self._log_error('CRD.spec.names.kind does not '
                                                        'match CSV.spec.crd.owned.kind')
                                        valid = False

                    if 'version' in csvOwnedCrd:
                        if 'spec' in crd:
                            if 'versions' in crd['spec']:
                                if csvOwnedCrd['version'] not in [
                                    v['name'] for v in crd['spec']['versions']
                                    if 'name' in v
                                ]:
                                    self._log_error('CSV.spec.crd.owned.version is '
                                                    'not in CRD.spec.versions list')
                                    valid = False
                            if 'version' in crd['spec']:
                                validCrdVersions[csvOwnedCrd['name']].append(
                                        csvOwnedCrd['version'] == crd['spec']['version']
                                )

                    if 'name' in csvOwnedCrd:
                        if 'spec' in crd:
                            if 'names' in crd['spec'] and 'group' in crd['spec']:
                                if 'plural' in crd['spec']['names']:
                                    if csvOwnedCrd['name'] != \
                                            crd['spec']['names']['plural'] + '.' + \
                                            crd['spec']['group']:
                                        self._log_error("`CRD.spec.names.plural`."
                                                        "`CRD.spec.group` does not "
                                                        "match "
                                                        "CSV.spec.crd.owned.name")
                                        valid = False

        for name, validVersions in validCrdVersions.items():
            # most likely we will have just one version per CRD; should we
            # have more than one single version, it is sufficient that just
            # one, usually the latest, matches.
            if not any(validVersions):
                self._log_error('CRD.spec.version does not match '
                                'CSV.spec.crd.owned.version')
                valid = False
        return valid

    def _csv_spec_install_validation(self, install):
        valid = True

        wantStrategyList = ["deployment"]

        # strategy check (required)
        if "strategy" in install:
            if install["strategy"] not in wantStrategyList:
                self._log_error(
                    "csv spec.install.strategy must be one of %s" % wantStrategyList)
                valid = False
        else:
            self._log_error("csv spec.install.strategy not defined")
            valid = False

        # spec check (required)
        if "spec" in install:
            # deployments check (required)
            if "deployments" in install["spec"]:
                deployments = install["spec"]["deployments"]
                if not isinstance(deployments, (list,)):
                    self._log_error(
                        "csv spec.install.spec.deployments should be a list")
                    valid = False
            else:
                self._log_error("csv spec.install.spec.deployments not defined")

            # permissions check (optional)
            try:
                permissions = install["spec"]["permissions"]
                if not isinstance(permissions, (list,)):
                    self._log_error("csv spec.install.spec.permissions should be a list")
                    valid = False
            except KeyError:
                pass

            # clusterPermissions check (optional)
            try:
                clusterPermissions = install["spec"]["clusterPermissions"]
                if not isinstance(clusterPermissions, (list,)):
                    self._log_error(
                        "csv spec.install.spec.clusterPermissions should be a list"
                    )
                    valid = False
            except KeyError:
                pass

        else:
            self._log_error("csv spec.install.spec not defined")
            valid = False

        return valid

    def _csv_metadata_validation(self, metadata):
        valid = True

        if "name" in metadata:
            logger.info("Evaluating csv %s", metadata["name"])
        else:
            self._log_error("csv metadata.name not defined.")
            valid = False

        if "annotations" in metadata:
            annotations = metadata["annotations"]

            annotationList = ["categories", "description",
                              "containerImage", "createdAt", "support"]

            for item in annotationList:
                if item not in annotations:
                    self._log_warning("csv metadata.annotations.%s not defined" % item)

            # check certified value's type in particular. should be string, not bool
            if "certified" not in annotations:
                self._log_warning("csv metadata.annotations.certified not defined.")
            else:
                isString = isinstance(annotations["certified"], str)
                if not isString:
                    self._log_error("metadata.annotations.certified is not of type"
                                    "string")
                    valid = False

            # if alm-examples is defined, check that its value is valid json
            if "alm-examples" in annotations:
                try:
                    json.loads(annotations["alm-examples"])
                except Exception:
                    self._log_error("metadata.annotations.alm-examples contains "
                                    "invalid json string")
                    valid = False

        else:
            self._log_warning("csv metadata.annotations not defined.")

        return valid

    def _pkgs_validation(self, bundle):
        valid = True
        logger.info("Validating packages.")

        bundle_metadata = bundle[self.metadataKey]
        bundleData = bundle[self.dataKey]
        pkgs = bundleData[self.pkgsKey]

        num_pkgs = len(pkgs)
        if num_pkgs != 1:
            self._log_error('Only 1 package is expected to exist per bundle, but got %d.',
                            num_pkgs)
            return False

        pkg = pkgs[0]
        pkg_file_name = self.get_filename_from_metadata(bundle_metadata, pkg)
        log_info['current_manifest_file'] = pkg_file_name

        if "packageName" in pkg:
            logger.info("Evaluating package %s", pkg["packageName"])
        else:
            self._log_error("packageName not defined.")
            valid = False

        if "channels" in pkg:
            channels = pkg["channels"]
            if len(channels) == 0:
                self._log_error("no package channels defined.")
                valid = False
            else:
                csvNames = []
                for csv in bundleData[self.csvKey]:
                    try:
                        csvName = csv["metadata"]["name"]
                        csvNames.append(csvName)
                    except KeyError:
                        pass
                for channel in channels:
                    if "name" not in channel:
                        self._log_error("package channel.name not defined.")
                        valid = False

                    if "currentCSV" not in channel:
                        self._log_error("package channel.currentCSV not defined.")
                    elif not self.nested and channel["currentCSV"] not in csvNames:
                        self._log_error("channel.currentCSV %s is not "
                                        "included in list of csvs",
                                        channel["currentCSV"])
                        valid = False

        else:
            self._log_error("package channels not defined.")
            valid = False

        return valid

    def _type_validation(self, bundle, typeName, validator, required):
        bundleData = bundle[self.dataKey]

        valid = True
        if typeName in bundleData:
            if len(bundleData[typeName]) != 0:
                valid = validator(bundle)
            elif required:
                self._log_error("Bundle does not contain any %s." % typeName)
                valid = False
        elif required:
            self._log_error("Bundle does not contain any %s." % typeName)
            valid = False

        return valid

    def _ui_validation_io(self, bundle):
        valid = True
        logger.info("Validating cluster service versions for operatorhub.io UI.")

        bundleData = bundle[self.dataKey]
        csvs = bundleData[self.csvKey]

        for csv in csvs:
            if self._ui_csv_fields_exist_validation_io(csv) is False:
                self._log_error("UI validation failed to verify required "
                                "fields for operatorhub.io exist.")
                valid = False

            if valid:
                if self._ui_csv_fields_format_validation_io(csv) is False:
                    self._log_error("UI validation failed to verify that required "
                                    "fields for operatorhub.io are properly formatted.")
                    valid = False

        return valid

    def _ui_csv_fields_exist_validation_io(self, csv):
        valid = True

        if "metadata" not in csv:
            self._log_error("csv metadata not defined.")
            valid = False
        else:
            if "name" not in csv["metadata"]:
                self._log_error("csv metadata.name not defined.")
                valid = False
            else:
                logger.info("Evaluating csv %s", csv["metadata"]["name"])

                for field in general_required_fields:
                    if field not in csv:
                        self._log_error("csv %s not defined.", field)
                        valid = False
                        return valid

                for field in metadata_required_fields:
                    if field["field"] not in csv["metadata"]:
                        if field["required"]:
                            self._log_error("csv metadata.%s not defined. %s",
                                            field["field"], field["description"])
                            valid = False
                            return valid
                        else:
                            self._log_warning("csv metadata.%s not defined. %s",
                                              field["field"], field["description"])

                for field in metadata_annotations_required_fields:
                    if field["field"] not in csv["metadata"]["annotations"]:
                        if field["required"]:
                            self._log_error("csv metadata.annotations.%s not defined. %s",
                                            field["field"], field["description"])
                            valid = False
                        else:
                            self._log_warning("csv metadata.annotations.%s not defined."
                                              "%s", field["field"], field["description"])

                for field in spec_required_fields:
                    if field["field"] not in csv["spec"]:
                        if field["required"]:
                            self._log_error("csv spec.%s not defined. %s",
                                            field["field"], field["description"])
                            valid = False
                        else:
                            self._log_warning("csv spec.%s not defined. %s",
                                              field["field"], field["description"])

        return valid

    def _ui_csv_fields_format_validation_io(self, csv):

        def is_url(field):
            if not v.url(field):
                return False
            return True

        def is_email(field):
            if not v.email(field):
                return False
            return True

        def is_version(field):
            try:
                semver.parse(field)
            except ValueError:
                return False
            return True

        def is_capability_level(field):
            levels = [
                "Basic Install",
                "Seamless Upgrades",
                "Full Lifecycle",
                "Deep Insights",
                "Auto Pilot"
            ]
            return field in levels

        def get_alm_kinds(alm_examples):
            res = []
            for example in alm_examples:
                res.append(example["kind"])
            return res

        def is_mediatype(mediatype):
            return mediatype in ["image/gif", "image/jpeg", "image/png", "image/svg+xml"]

        def is_category(category):
            valid_categories = [
                "AI/Machine Learning",
                "Application Runtime",
                "Big Data",
                "Cloud Provider",
                "Developer Tools",
                "Database",
                "Integration & Delivery",
                "Logging & Tracing",
                "Monitoring",
                "Networking",
                "OpenShift Optional",
                "Security",
                "Storage",
                "Streaming & Messaging"
            ]
            return category in valid_categories

        valid = True

        spec = csv["spec"]
        provider = spec["provider"]

        if "annotations" in csv["metadata"]:
            annotations = csv["metadata"]["annotations"]

            # alm-examples check based on crd field
            if "customresourcedefinitions" in spec:
                if "owned" in spec["customresourcedefinitions"]:
                    crds = spec["customresourcedefinitions"]["owned"]
                    if "alm-examples" in annotations:
                        alm_kinds = get_alm_kinds(json.loads(annotations["alm-examples"]))
                        for crd in crds:
                            if crd["kind"] not in alm_kinds:
                                self._log_warning("%s CRD does not have an entry in "
                                                  "alm-examples - please add such an "
                                                  "example CR.", crd["kind"])
                    else:
                        self._log_warning("You should have alm-examples "
                                          "for every owned CRD")

        # provider check
        if isinstance(provider, (dict,)):
            if len(provider) != 1:
                self._log_error("csv.spec.provider should be a singleton list.")
                valid = False
            else:
                if "name" not in provider or len(provider.keys()) != 1:
                    self._log_error("csv.spec.provider element should "
                                    "have a single field \"name\".")
                    valid = False
        else:
            self._log_error("csv.spec.provider should contain a \"name\" field.")
            valid = False

        # maintainers check
        if "maintainer" in spec:
            if isinstance(spec["maintainers"], (list,)):
                for maintainer in spec["maintainers"]:
                    if "name" not in maintainer or "email" not in maintainer:
                        self._log_error("csv.spec.maintainers element should contain "
                                        "both name and email")
                        valid = False
                    else:
                        if not is_email(maintainer["email"]):
                            self._log_error("%s is not a valid email",
                                            maintainer["email"])
                            valid = False
            else:
                self._log_error("csv.spec.maintainers must be a list "
                                "of name & email pairs.")
                valid = False

        # links check
        if "links" in spec:
            if isinstance(spec["links"], (list,)):
                for link in spec["links"]:
                    if "name" not in link or "url" not in link:
                        self._log_error("csv.spec.links element should contain "
                                        "both name and url")
                        valid = False
                    else:
                        if not is_url(link["url"]):
                            self._log_error("%s is not a valid url", link["url"])
                            valid = False
            else:
                self._log_error("csv.spec.links must be a list of name & url pairs.")
                valid = False

        # version check
        if not is_version(spec["version"]):
            self._log_error("spec.version %s is not a valid semver "
                            "(example of a valid semver is: 1.0.12)",
                            spec["version"])
            valid = False

        # capabilities check
        if "annotations" in csv["metadata"]:
            annotations = csv["metadata"]["annotations"]
            if "capabilities" in annotations:
                if not is_capability_level(annotations["capabilities"]):
                    self._log_error("metadata.annotations.capabilities %s is not a "
                                    "valid capabilities level",
                                    annotations["capabilities"])
                    valid = False

        # icon check
        if "icon" in spec:
            icons = spec["icon"]
            if isinstance(icons, (list,)):
                if len(icons) == 1:
                    icon = icons[0]
                    if len(icon.keys()) == 2:
                        if "base64data" in icon and "mediatype" in icon:
                            if not is_mediatype(icon["mediatype"]):
                                self._log_error(
                                    "spec.icon[0].mediatype %s is not a valid mediatype. "
                                    "It must be one of \"image/gif\", \"image/jpeg\", "
                                    "\"image/png\", \"image/svg+xml\"", icon["mediatype"]
                                )
                                valid = False
                        else:
                            self._log_error("spec.icon[0] must contain the fields "
                                            "\"base64data\" and \"mediatype\".")
                            valid = False
                    else:
                        self._log_error("spec.icon can only contain two fields: "
                                        "\"base64data\" and \"mediatype\"")
                        valid = False
                else:
                    self._log_error("spec.icon should be a singleton list")
                    valid = False
            else:
                self._log_error("spec.icon should be a list")
                valid = False

        # categories check
        if "categories" in annotations:
            categories = annotations["categories"].split(',')
            for category in categories:
                if not is_category(category.lstrip()):
                    self._log_error(
                        "category %s is not a valid category",
                        category.lstrip()
                    )
                    valid = False

        return valid
