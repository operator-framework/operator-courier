import logging
import json
import semver

import validators as v

from .const_io import (
    general_required_fields,
    metadata_required_fields,
    metadata_annotations_required_fields,
    spec_required_fields)

logger = logging.getLogger(__name__)


class ValidateCmd():
    dataKey = "data"
    crdKey = "customResourceDefinitions"
    csvKey = "clusterServiceVersions"
    pkgsKey = "packages"

    err_invalid_category = 'invalid_category'
    err_missing_owned_crd_field_in_csv = 'missing_owned_crd_field_in_csv'
    err_invalid_alm_examples = 'invalid_alm_examples'
    err_missing_field_for_operatorhub_io = 'missing_field_for_operatorhub_io'
    err_csv_field_issue = 'csv_field_issue'

    err_message_kind_to_ref_urls = {
        err_invalid_category: ['https://github.com/operator-framework/community-operators'
                               '/blob/master/docs/required-fields.md#categories'],
        err_missing_owned_crd_field_in_csv: ['https://github.com/operator-framework/'
                                             'operator-lifecycle-manager/blob/master/'
                                             'Documentation/design/building-your-csv.md'
                                             '#owned-crds'],
        err_invalid_alm_examples: ['https://github.com/operator-framework/'
                                   'operator-lifecycle-manager/blob/master/Documentation/'
                                   'design/building-your-csv.md#crd-templates'],
        err_missing_field_for_operatorhub_io: ['https://github.com/operator-framework/'
                                               'community-operators/blob/master/docs/'
                                               'required-fields.md#'
                                               'required-fields-for-operatorhubio'],
        err_csv_field_issue: ['https://github.com/operator-framework/community-'
                              'operators/blob/master/docs/required-fields.md',
                              'https://github.com/operator-framework/operator-'
                              'lifecycle-manager/blob/master/Documentation/design/'
                              'building-your-csv.md']
    }

    def __init__(self, ui_validate_io=False):
        self.ui_validate_io = ui_validate_io
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

    def _log_error(self, message, message_kind='', *args, **kwargs):
        """_log_error prints the message to the logger as an error
        and appends it to a dictionary that can be printed to the
        screen for automation purposes
         :param message: The message to log
        """
        if message_kind in self.err_message_kind_to_ref_urls:
            message += ' See links below for more details and examples:\n'
            for url in self.err_message_kind_to_ref_urls[message_kind]:
                message += f'\n{url}'

        self.validation_json['errors'].append(message % args)
        logger.error(message, *args, **kwargs)

    def validate(self, bundle, repository=None):
        """validate takes a bundle as a dictionary and returns a boolean value that
        describes if the bundle is valid. It also logs verification information when
        there are invalid sections in the bundle.

        :param bundle: Dictionary of bundle value
        :param repository: Repository name for the application
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

        validationDict[self.crdKey] = self._type_validation(bundleData, self.crdKey,
                                                            self._crd_validation, False)
        validationDict[self.csvKey] = self._type_validation(bundleData, self.csvKey,
                                                            self._csv_validation, True)
        validationDict[self.pkgsKey] = self._type_validation(bundleData, self.pkgsKey,
                                                             self._pkgs_validation, True)
        if self.ui_validate_io:
            validationDict[self.csvKey] &= self._type_validation(
                bundleData, self.csvKey, self._ui_validation_io, True)
        if validationDict[self.pkgsKey] and repository is not None:
            packageName = bundleData['packages'][0]['packageName']
            if repository != packageName:
                self._log_error(f'The packageName ({packageName}) in bundle does not '
                                f'match repository name ({repository}) provided '
                                f'as command line argument.')
                validationDict[self.pkgsKey] = False

        valid = True
        for key, value in validationDict.items():
            if value is False:
                valid = False

        return valid

    def _crd_validation(self, bundleData):
        logger.info("Validating custom resource definitions.")
        valid = True

        crds = bundleData[self.crdKey]

        for crd in crds:
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
                if "version" not in crd['spec']:
                    self._log_error("crd spec.version not defined.")
                    valid = False

        return valid

    def _csv_validation(self, bundleData):
        valid = True
        logger.info("Validating cluster service versions.")

        csvs = bundleData[self.csvKey]

        for csv in csvs:
            if "metadata" in csv:
                if self._csv_metadata_validation(csv["metadata"]) is False:
                    valid = False
            else:
                self._log_error("csv metadata not defined.",
                                self.err_csv_field_issue)
                valid = False

            if "apiVersion" not in csv:
                self._log_error("csv apiVersion not defined.",
                                self.err_csv_field_issue)
                valid = False

            if "spec" in csv:
                if self._csv_spec_validation(csv["spec"], bundleData) is False:
                    valid = False
            else:
                self._log_error("csv spec not defined.",
                                self.err_csv_field_issue)
                valid = False

        return valid

    def _csv_spec_validation(self, spec, bundleData):
        valid = True

        warnSpecList = ["displayName", "description", "icon",
                        "version", "provider", "maturity"]

        for item in warnSpecList:
            if item not in spec:
                self._log_warning("csv spec.%s not defined" % item)

        if "installModes" not in spec:
            self._log_error("csv spec.installModes not defined.",
                            self.err_csv_field_issue)
            valid = False

        if "install" not in spec:
            self._log_error("csv spec.install not defined.",
                            self.err_csv_field_issue)
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
                self._log_error("spec.customresourcedefinitions.owned "
                                "not defined for csv.",
                                self.err_missing_owned_crd_field_in_csv)
                return False

            for csvOwnedCrd in customresourcedefinitions["owned"]:
                if "name" not in csvOwnedCrd:
                    self._log_error("name not defined for item in "
                                    "spec.customresourcedefinitions.",
                                    self.err_missing_owned_crd_field_in_csv)
                    valid = False
                elif csvOwnedCrd["name"] not in crdList:
                    self._log_error(f'custom resource definition {csvOwnedCrd["name"]} '
                                    f'referenced in csv not defined '
                                    f'in root list of crds.',
                                    self.err_missing_owned_crd_field_in_csv)
                    valid = False

                if "kind" not in csvOwnedCrd:
                    self._log_error("kind not defined for item in "
                                    "spec.customresourcedefinitions.",
                                    self.err_missing_owned_crd_field_in_csv)
                    valid = False
                if "version" not in csvOwnedCrd:
                    self._log_error("version not defined for item in "
                                    "spec.customresourcedefinitions.",
                                    self.err_missing_owned_crd_field_in_csv)
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
                            if 'version' in crd['spec']:
                                if csvOwnedCrd['version'] != crd['spec']['version']:
                                    self._log_error('CRD.spec.version does not match '
                                                    'CSV.spec.crd.owned.version')
                                    valid = False

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
        return valid

    def _csv_metadata_validation(self, metadata):
        valid = True

        if "name" in metadata:
            logger.info("Evaluating csv %s", metadata["name"])
        else:
            self._log_error("csv metadata.name not defined.",
                            self.err_csv_field_issue)
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
                except KeyError:
                    self._log_error("metadata.annotations.alm-examples contains "
                                    "invalid json string.",
                                    self.err_invalid_alm_examples)
                    valid = False

        else:
            self._log_warning("csv metadata.annotations not defined.")

        return valid

    def _pkgs_validation(self, bundleData):
        valid = True
        logger.info("Validating packages.")

        pkgs = bundleData[self.pkgsKey]

        num_pkgs = len(pkgs)
        if num_pkgs != 1:
            self._log_error(f'Only 1 package is expected to exist per bundle, '
                            f'but got {num_pkgs}.')
            return False

        pkg = pkgs[0]

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
                    else:
                        if channel["currentCSV"] not in csvNames:
                            self._log_error(f'channel.currentCSV {channel["currentCSV"]}'
                                            f' is not included in list of csvs')
                            valid = False

        else:
            self._log_error("package channels not defined.")
            valid = False

        return valid

    def _type_validation(self, bundleData, typeName, validator, required):
        valid = True
        if typeName in bundleData:
            if len(bundleData[typeName]) != 0:
                valid = validator(bundleData)
            elif required:
                self._log_error(f"Bundle does not contain any {typeName}.")
                valid = False
        elif required:
            self._log_error(f"Bundle does not contain any {typeName}.")
            valid = False

        return valid

    def _ui_validation_io(self, bundleData):
        valid = True
        logger.info("Validating cluster service versions for operatorhub.io UI.")

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
            self._log_error("csv metadata not defined.",
                            self.err_csv_field_issue)
            valid = False
        else:
            if "name" not in csv["metadata"]:
                self._log_error("csv metadata.name not defined.",
                                self.err_csv_field_issue)
                valid = False
            else:
                logger.info("Evaluating csv %s", csv["metadata"]["name"])

                for field in general_required_fields:
                    if field not in csv:
                        self._log_error(f"csv {field} not defined.",
                                        self.err_csv_field_issue)
                        valid = False
                        return valid

                for field in metadata_required_fields:
                    if field["field"] not in csv["metadata"]:
                        if field["required"]:
                            self._log_error(f'csv metadata.{field["field"]} not defined. '
                                            f'{field["description"]}',
                                            self.err_missing_field_for_operatorhub_io)
                            valid = False
                            return valid
                        else:
                            self._log_warning(f'csv metadata.{field["field"]} not '
                                              f'defined. {field["description"]}')

                for field in metadata_annotations_required_fields:
                    if field["field"] not in csv["metadata"]["annotations"]:
                        if field["required"]:
                            self._log_error(f'csv metadata.annotations.{field["field"]} '
                                            f'not defined. {field["description"]}',
                                            self.err_missing_field_for_operatorhub_io)
                            valid = False
                        else:
                            self._log_warning(f'csv metadata.annotations.{field["field"]}'
                                              f' not defined. {field["description"]}')

                for field in spec_required_fields:
                    if field["field"] not in csv["spec"]:
                        if field["required"]:
                            self._log_error(f'csv spec.{field["field"]} not defined. '
                                            f'{field["description"]}',
                                            self.err_missing_field_for_operatorhub_io)
                            valid = False
                        else:
                            self._log_warning(f'csv spec.{field["field"]} not defined. '
                                              f'{field["description"]}')

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
                "Big Data",
                "Cloud Provider",
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
        annotations = csv["metadata"]["annotations"]

        # alm-examples check based on crd field
        if "customresourcedefinitions" in spec:
            if "owned" in spec["customresourcedefinitions"]:
                crds = spec["customresourcedefinitions"]["owned"]
                if "alm-examples" in annotations:
                    alm_kinds = get_alm_kinds(json.loads(annotations["alm-examples"]))
                    for crd in crds:
                        if crd["kind"] not in alm_kinds:
                            self._log_error(f'{crd["kind"]} CRD does not have an entry '
                                            f'in alm-examples - please add such an '
                                            f'example CR.',
                                            self.err_invalid_alm_examples)
                            valid = False
                else:
                    self._log_error("You should have alm-examples for every owned CRD.",
                                    self.err_invalid_alm_examples)
                    valid = False

        # provider check
        if isinstance(provider, (dict,)):
            if len(provider) != 1:
                self._log_error("csv.spec.provider should be a singleton list.",
                                self.err_csv_field_issue)
                valid = False
            else:
                if "name" not in provider or len(provider.keys()) != 1:
                    self._log_error("csv.spec.provider element should "
                                    "have a single field \"name\".",
                                    self.err_csv_field_issue)
                    valid = False
        else:
            self._log_error("csv.spec.provider should contain a \"name\" field.",
                            self.err_csv_field_issue)
            valid = False

        # maintainers check
        if isinstance(spec["maintainers"], (list,)):
            for maintainer in spec["maintainers"]:
                if "name" not in maintainer or "email" not in maintainer:
                    self._log_error("csv.spec.maintainers element should contain "
                                    "both name and email.",
                                    self.err_csv_field_issue)
                    valid = False
                else:
                    if not is_email(maintainer["email"]):
                        self._log_error(f'{maintainer["email"]} is not a valid email')
                        valid = False
        else:
            self._log_error("csv.spec.maintainers must be a list of name & email pairs.",
                            self.err_csv_field_issue)
            valid = False

        # links check
        if isinstance(spec["links"], (list,)):
            for link in spec["links"]:
                if "name" not in link or "url" not in link:
                    self._log_error("csv.spec.links element should contain "
                                    "both name and url.",
                                    self.err_csv_field_issue)
                    valid = False
                else:
                    if not is_url(link["url"]):
                        self._log_error(f'{link["url"]} is not a valid url')
                        valid = False
        else:
            self._log_error("csv.spec.links must be a list of name & url pairs.",
                            self.err_csv_field_issue)
            valid = False

        # version check
        if not is_version(spec["version"]):
            self._log_error(f'spec.version {spec["version"]} is not a valid semver '
                            f'(example of a valid semver is: 1.0.12)')
            valid = False

        # capabilities check
        if not is_capability_level(annotations["capabilities"]):
            self._log_error(f'metadata.annotations.capabilities '
                            f'{annotations["capabilities"]} is not a '
                            f'valid capabilities level.',
                            self.err_missing_field_for_operatorhub_io)
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
                                    f'spec.icon[0].mediatype {icon["mediatype"]} is not '
                                    f'a valid mediatype. It must be one of "image/gif", '
                                    f'"image/jpeg", "image/png", "image/svg+xml".',
                                    self.err_missing_field_for_operatorhub_io
                                )
                                valid = False
                        else:
                            self._log_error("spec.icon[0] must contain the fields "
                                            "\"base64data\" and \"mediatype\".",
                                            self.err_missing_field_for_operatorhub_io)
                            valid = False
                    else:
                        self._log_error("spec.icon can only contain two fields: "
                                        "\"base64data\" and \"mediatype\".",
                                        self.err_missing_field_for_operatorhub_io)
                        valid = False
                else:
                    self._log_error("spec.icon should be a singleton list.",
                                    self.err_missing_field_for_operatorhub_io)
                    valid = False
            else:
                self._log_error("spec.icon should be a list.",
                                self.err_missing_field_for_operatorhub_io)
                valid = False

        # categories check
        if "categories" in annotations:
            categories = annotations["categories"].split(',')
            for category in categories:
                if not is_category(category.lstrip()):
                    self._log_error(
                        f"category {category.lstrip()} is not a valid category.",
                        self.err_invalid_category
                    )
                    valid = False

        return valid
