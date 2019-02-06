import yaml

def get_operator_artifact_type(operatorArtifactString):
    """get_operator_artifact_type takes a yaml string and determines if it is one of the 
    expected bundle types: ClusterServiceVersion, CustomResourceDefinition, or Package.

    :param operatorArtifactString: Yaml string to type check
    """
    operatorArtifact = yaml.safe_load(operatorArtifactString)
    if isinstance(operatorArtifact, dict):
        if "packageName" in operatorArtifact:
            return "Package"
        elif "kind" in operatorArtifact:
            if operatorArtifact["kind"] in ("ClusterServiceVersion", "CustomResourceDefinition"):
                return operatorArtifact["kind"]
    raise ValueError('Courier requires valid CSV, CRD, and Package files')
