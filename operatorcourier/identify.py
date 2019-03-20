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
        artifact_type, artifact_name = None, None
        if isinstance(operatorArtifact, dict):
            if "packageName" in operatorArtifact:
                artifact_type = "Package"
                artifact_name = operatorArtifact['packageName']
            elif operatorArtifact.get("kind") in ("ClusterServiceVersion",
                                                  "CustomResourceDefinition"):
                artifact_type = operatorArtifact["kind"]
                artifact_name = operatorArtifact['metadata']['name']
            if artifact_type is not None:
                logger.info('Parsed %s: %s', artifact_type, artifact_name)
                return artifact_type

        msg = 'Courier requires valid CSV, CRD, and Package files'
        logger.error(msg)
        raise OpCourierBadArtifact(msg)
