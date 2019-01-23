import yaml

def get_operator_artifact_type(operatorArtifactString):
    operatorArtifact = yaml.load(operatorArtifactString)
    if isinstance(operatorArtifact, dict):
        if "packageName" in operatorArtifact:
            return "packages"
        elif "kind" in operatorArtifact:
            if operatorArtifact["kind"] == "ClusterServiceVersion": 
                return "clusterServiceVersions"
            elif operatorArtifact["kind"] == "CustomResourceDefinition":
                return "customResourceDefinitions"
    return "invalid"
