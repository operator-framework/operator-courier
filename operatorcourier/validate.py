import logging
import json
import re

import validators as v

from .const_io import general_required_fields, metadata_required_fields, metadata_annotations_required_fields, spec_required_fields

logger = logging.getLogger(__name__)


class ValidateCmd():
    dataKey = "data"
    crdKey = "customResourceDefinitions"
    csvKey = "clusterServiceVersions"
    pkgsKey = "packages"

    def __init__(self, ui_validate_io=False):
        self.ui_validate_io = ui_validate_io
        pass

    def validate(self, bundle):
        """validate takes a bundle as a dictionary and returns a boolean value that
        describes if the bundle is valid. It also logs verification information when
        there are invalid sections in the bundle.

        :param bundle: Dictionary of bundle value
        """
        logger.info("Validating bundle.")

        return self._bundle_validation(bundle)

    def _bundle_validation(self, bundle):
        validationDict = dict()

        if self.dataKey not in bundle:
            logger.error("Bundle does not contain base data field.")
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
                    logger.error("crd metadata.name not defined.")
                    valid = False
            else:
                logger.error("crd metadata not defined.")
                valid = False

            if "apiVersion" not in crd:
                logger.error("crd apiVersion not defined.")
                valid = False

            if "spec" not in crd:
                logger.error("crd spec not defined.")
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
                logger.error("csv metadata not defined.")
                valid = False

            if "apiVersion" not in csv:
                logger.error("csv apiVersion not defined.")
                valid = False

            if "spec" in csv:
                if self._csv_spec_validation(csv["spec"], bundleData) is False:
                    valid = False
            else:
                logger.error("csv spec not defined.")
                valid = False

        return valid

    def _csv_spec_validation(self, spec, bundleData):
        valid = True

        warnSpecList = ["displayName", "description", "icon",
                        "version", "provider", "maturity"]

        for item in warnSpecList:
            if item not in spec:
                logger.warning("csv spec.%s not defined" % item)

        if "installModes" not in spec:
            logger.error("csv spec.installModes not defined")
            valid = False

        if "install" not in spec:
            logger.error("csv spec.install not defined")
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
                logger.error("spec.customresourcedefinitions.owned not defined for csv")
                valid = False
            else:
                for crd in customresourcedefinitions["owned"]:
                    if "name" not in crd:
                        logger.error("name not defined for item in "
                                     "spec.customresourcedefinitions.")
                        valid = False
                    else:
                        if crd["name"] not in crdList:
                            logger.error("custom resource definition referenced "
                                         "in csv not defined in root list of crds")

        return valid

    def _csv_metadata_validation(self, metadata):
        valid = True

        if "name" in metadata:
            logger.info("Evaluating csv %s", metadata["name"])
        else:
            logger.error("csv metadata.name not defined.")
            valid = False

        if "annotations" in metadata:
            annotations = metadata["annotations"]

            annotationList = ["categories", "description",
                              "containerImage", "createdAt", "support"]

            for item in annotationList:
                if item not in annotations:
                    logger.warning("csv metadata.annotations.%s not defined" % item)

            # check certified value's type in particular. should be string, not bool
            if "certified" not in annotations:
                logger.warning("csv metadata.annotations.certified not defined.")
            else:
                isString = isinstance(annotations["certified"], str)
                if not isString:
                    logger.error("metadata.annotations.certified is not of type string")
                    valid = False

            # if alm-examples is defined, check that its value is valid json
            if "alm-examples" in annotations:
                try:
                    json.loads(annotations["alm-examples"])
                except KeyError:
                    logger.error("metadata.annotations.alm-examples contains "
                                 "invalid json string")
                    valid = False

        else:
            logger.warning("csv metadata.annotations not defined.")

        return valid

    def _pkgs_validation(self, bundleData):
        valid = True
        logger.info("Validating packages.")

        pkgs = bundleData[self.pkgsKey]

        for pkg in pkgs:
            if "packageName" in pkg:
                logger.info("Evaluating package %s", pkg["packageName"])
            else:
                logger.error("packageName not defined.")
                valid = False

            if "channels" in pkg:
                channels = pkg["channels"]
                if len(channels) == 0:
                    logger.error("no package channels defined.")
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
                            logger.error("package channel.name not defined.")
                            valid = False

                        if "currentCSV" not in channel:
                            logger.error("package channel.currentCSV not defined.")
                        else:
                            if channel["currentCSV"] not in csvNames:
                                logger.error("channel.currentCSV %s is not "
                                             "included in list of csvs",
                                             channel["currentCSV"])
                                valid = False

            else:
                logger.error("package channels not defined.")
                valid = False

        return valid

    def _type_validation(self, bundleData, typeName, validator, required):
        valid = True
        if typeName in bundleData:
            if len(bundleData[typeName]) != 0:
                valid = validator(bundleData)
            elif required:
                logger.error("Bundle does not contain any %s." % typeName)
                valid = False
        elif required:
            logger.error("Bundle does not contain any %s." % typeName)
            valid = False

        return valid

    def _ui_validation_io(self, bundleData):
        valid = True
        logger.info("Validating cluster service versions for operatorhub.io UI.")

        csvs = bundleData[self.csvKey]

        for csv in csvs:
            if self._ui_csv_fields_exist_validation_io(csv) is False:
                logger.error("UI validation failed to verify required fields for operatorhub.io exist.")
                valid = False

            if valid:
                if self._ui_csv_fields_format_validation_io(csv) is False:
                    logger.error("UI validation failed to verify that required fields for operatorhub.io are properly formatted.")
                    valid = False

        return valid

    def _ui_csv_fields_exist_validation_io(self, csv):
        valid = True

        if "metadata" not in csv:
            logger.error("csv metadata not defined.")
            valid = False
        else:
            if "name" not in csv["metadata"]:
                logger.error("csv metadata.name not defined.")
                valid = False
            else:
                logger.info("Evaluating csv %s", csv["metadata"]["name"])

                for field in general_required_fields:
                    if field not in csv:
                        logger.error("csv %s not defined.", field)
                        valid = False
                        return valid

                for field in metadata_required_fields:
                    if field["field"] not in csv["metadata"]:
                        if field["required"]:
                            logger.error("csv metadata.%s not defined. %s", field["field"], field["description"])
                            valid = False
                            return valid
                        else:
                            logger.warning("csv metadata.%s not defined. %s", field["field"], field["description"])

                for field in metadata_annotations_required_fields:
                    if field["field"] not in csv["metadata"]["annotations"]:
                        if field["required"]:
                            logger.error("csv metadata.annotations.%s not defined. %s", field["field"], field["description"])
                            valid = False
                        else:
                            logger.warning("csv metadata.annotations.%s not defined. %s", field["field"], field["description"])

                for field in spec_required_fields:
                    if field["field"] not in csv["spec"]:
                        if field["required"]:
                            logger.error("csv spec.%s not defined. %s", field["field"], field["description"])
                            valid = False
                        else:
                            logger.warning("csv spec.%s not defined. %s", field["field"], field["description"])

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
            pattern1 = re.compile(r'v(\d+\.)(\d+\.)(\d)')
            pattern2 = re.compile(r'(\d+\.)(\d+\.)(\d)')
            return pattern1.match(field) or pattern2.match(field)

        def is_capability_level(field):
            levels = [
                "Basic Install",
                "Seamless Upgrades",
                "Full Lifecycle",
                "Deep Insight",
                "Auto Pilot"
            ]
            return field in levels

        def get_alm_kinds(alm_examples):
            res = []
            for example in alm_examples:
                res.append(example["kind"])
            return res

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
                            logger.error("%s CRD does not have an entry in alm-examples - please add such an example CR.", crd["kind"])
                            valid = False
                else:
                    logger.error("You should have alm-examples for every owned CRD")
                    valid = False

        # provider check
        if isinstance(provider, (dict,)):
            if len(provider) != 1:
                logger.error("csv.spec.provider should be a singleton list.")
                valid = False
            else:
                if "name" not in provider or len(provider.keys()) != 1:
                    logger.error("csv.spec.provider element should have a single field \"name\".")
                    valid = False
        else:
            logger.error("csv.spec.provider should contain a \"name\" field.")
            valid = False

        # maintainers check
        if isinstance(spec["maintainers"], (list,)):
            for maintainer in spec["maintainers"]:
                if "name" not in maintainer or "email" not in maintainer:
                    logger.error("csv.spec.maintainers element should contain both name and email")
                    valid = False
                else:
                    if not is_email(maintainer["email"]):
                        logger.error("%s is not a valid email", maintainer["email"])
                        valid = False
        else:
            logger.error("csv.spec.maintainers must be a list of name & email pairs.")
            valid = False

        # links check
        if isinstance(spec["links"], (list,)):
            for link in spec["links"]:
                if "name" not in link or "url" not in link:
                    logger.error("csv.spec.links element should contain both name and url")
                    valid = False
                else:
                    if not is_url(link["url"]):
                        logger.error("%s is not a valid url", link["url"])
                        valid = False
        else:
            logger.error("csv.spec.links must be a list of name & url pairs.")
            valid = False

        # version check
        if not is_version(spec["version"]):
            logger.error("spec.version %s is not a valid version (example of a valid version is: v1.0.12)", spec["version"])
            valid = False

        # capabilities check
        if not is_capability_level(annotations["capabilities"]):
            logger.error("metadata.annotations.capabilities %s is not a valid capabilities level", annotations["capability"])
            valid = False

        return valid
