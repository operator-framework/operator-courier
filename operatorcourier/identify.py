from yaml import safe_load
from yaml import MarkedYAMLError
import logging
from operatorcourier.errors import OpCourierBadYaml
from operatorcourier.manifest_parser import CRD_STR, CSV_STR, PKG_STR

logger = logging.getLogger(__name__)

UNKNOWN_FILE = "Unknown"


def get_operator_artifact_type(operatorArtifactString):
    """get_operator_artifact_type takes a yaml string and determines if it is
    one of the expected bundle types.

    :param operatorArtifactString: Yaml string to type check
    """

    # Default to unknown file unless identified
    artifact_type = UNKNOWN_FILE

    try:
        operatorArtifact = safe_load(operatorArtifactString)
    except MarkedYAMLError:
        msg = "Courier requires valid input YAML files"
        logger.error(msg)
        raise OpCourierBadYaml(msg)
    else:
        if isinstance(operatorArtifact, dict):
            if "packageName" in operatorArtifact:
                artifact_type = PKG_STR
            elif operatorArtifact.get("kind") in {CRD_STR, CSV_STR}:
                artifact_type = operatorArtifact["kind"]
        return artifact_type
