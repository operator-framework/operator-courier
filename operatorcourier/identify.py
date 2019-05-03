from yaml import safe_load
from yaml import MarkedYAMLError
import logging
from operatorcourier.errors import OpCourierBadYaml, OpCourierBadArtifact

logger = logging.getLogger(__name__)


def get_operator_artifact_type(operatorArtifactString):
    """get_operator_artifact_type takes a yaml string and determines if it is
    one of the expected bundle types: ClusterServiceVersion,
    CustomResourceDefinition, or Package.

    :param operatorArtifactString: Yaml string to type check
    """
    try:
        operatorArtifact = safe_load(operatorArtifactString)
    except MarkedYAMLError:
        msg = "Courier requires valid input YAML files"
        logger.error(msg)
        raise OpCourierBadYaml(msg)
    else:
        artifact_type = None
        if isinstance(operatorArtifact, dict):
            if "packageName" in operatorArtifact:
                artifact_type = "Package"
            elif operatorArtifact.get("kind") in ("ClusterServiceVersion",
                                                  "CustomResourceDefinition"):
                artifact_type = operatorArtifact["kind"]
            if artifact_type is not None:
                return artifact_type

        msg = 'Courier requires valid CSV, CRD, and Package files'
        logger.error(msg)
        raise OpCourierBadArtifact(msg)
