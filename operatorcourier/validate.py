import logging
import json

logger = logging.getLogger(__name__)

class ValidateCmd():
    dataKey = "data"
    crdKey = "customResourceDefinitions"
    csvKey = "clusterServiceVersions"
    pkgsKey = "packages"

    def __init__(self):
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
            #break here because there's nothing else to learn
            return False

        bundleData = bundle[self.dataKey]

        validationDict[self.crdKey] = self._type_validation(bundleData, self.crdKey, self._crd_validation, False)  
        validationDict[self.csvKey] = self._type_validation(bundleData, self.csvKey, self._csv_validation, True)
        validationDict[self.pkgsKey] = self._type_validation(bundleData, self.pkgsKey, self._pkgs_validation, True)

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

        warnSpecList = ["displayName", "description", "icon", "version", "provider", "maturity"]
        
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
                        logger.error("name not defined for item in spec.customresourcedefinitions.")
                        valid = False
                    else:
                        if crd["name"] not in crdList:
                            logger.error("custom resource definition referenced in csv not defined in root list of crds")

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

            annotationList = ["categories", "description", "containerImage", "createdAt", "support"]

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
                    valid_json = json.loads(annotations["alm-examples"])
                except KeyError:
                    logger.error("metadata.annotations.alm-examples contains invalid json string")
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
                                logger.error("channel.currentCSV %s is not included in list of csvs")
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
